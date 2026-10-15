"""用真实编排器和工具核验讲稿；模型返回由测试传输替代，不调用外部服务。"""
import ast
import copy
import hashlib
import inspect
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT.parent / 'code-app-example' / 'backend'
sys.path.insert(0, str(BACKEND))

import db
from ai import chat, tools
from ontology.registry import load_ontology, registry
from sql_readonly.query import query_readonly

CONFIG = {'configured': True, 'base_url': 'https://example.invalid', 'api_key': 'test-key',
          'model_id': 'test-model', 'max_tokens': 1024}
EVIDENCE = {}


def tool_call(name, args, identifier):
    return {'id': identifier, 'type': 'function',
            'function': {'name': name, 'arguments': json.dumps(args, ensure_ascii=False)}}


def response(calls=None):
    message = {'role': 'assistant', 'content': None if calls else '非流式阶段的试答'}
    if calls:
        message['tool_calls'] = calls
    return {'choices': [{'message': message}]}


def observe(replies, history=None, configured=True):
    """仅替换模型传输与配置，消息循环、提示词、SQL、工具均执行真实代码。"""
    sequence = iter(replies)
    requests = []

    def decide(base_url, api_key, model_id, messages, **kwargs):
        requests.append({'阶段': '决策', 'messages': copy.deepcopy(messages),
                         '工具数': len(kwargs.get('tools', []))})
        return next(sequence)

    def stream(base_url, api_key, model_id, messages, **kwargs):
        requests.append({'阶段': '流式', 'messages': copy.deepcopy(messages),
                         '携带工具定义': 'tools' in kwargs})
        return iter(['查询已完成，', '请查看统计结果。'])

    config = {**CONFIG, 'configured': configured}
    with patch.object(chat.ai_config, 'get_config', return_value=config), \
         patch.object(chat.llm, 'chat_completion', side_effect=decide), \
         patch.object(chat.llm, 'stream_chat_completion', side_effect=stream), \
         patch('requests.post', side_effect=AssertionError('分析禁止发起外部请求')):
        events = list(chat.run_chat('按部门统计合同总金额，并打开合同查询。', history or [],
                                    {'id': 101, 'username': 'test-user'}))
    return requests, events


def verify_context_and_direct_reply():
    history = [{'role': 'user' if n % 2 == 0 else 'assistant', 'content': f'历史消息{n}'} for n in range(14)]
    requests, events = observe([response()], history)
    messages = requests[0]['messages']
    assert len(messages) == 12, '系统提示词 + 最近10条文本 + 当前问题，共12条'
    assert [m['content'] for m in messages[1:-1]] == [m['content'] for m in history[-10:]]
    assert '本体模型语义' in messages[0]['content'] and '数据库表结构' in messages[0]['content']
    assert len(requests) == 2 and not requests[-1]['携带工具定义']
    assert all(m['content'] != '非流式阶段的试答' for m in requests[-1]['messages'])
    assert [name for name, _ in events] == ['message_start', 'delta', 'delta', 'message_end']
    EVIDENCE['文本记忆与两段生成'] = {'历史输入': 14, '历史实际保留': 10, '模型请求': 2,
                                  '首个无工具回答进入后续上下文': False}


def verify_two_tools_and_protocols():
    sql = 'SELECT d.department_name AS 部门, SUM(c.total_amount) AS 合同总金额 FROM contract c JOIN department d ON d.id=c.department_id WHERE c.flag=1 GROUP BY d.id ORDER BY d.id'
    calls = [tool_call('readonly_sql_query', {'sql': sql, 'chart_type': 'bar'}, 'call-sql'),
             tool_call('navigate_to_page', {'page_name': '合同查询'}, 'call-navigation')]
    requests, events = observe([response(calls), response()])
    assert len(requests) == 3
    tool_messages = [m for m in requests[-1]['messages'] if m['role'] == 'tool']
    assert [m['tool_call_id'] for m in tool_messages] == ['call-sql', 'call-navigation']
    first = json.loads(tool_messages[0]['content'])
    assert set(first) == {'text', 'data'} and len(first['data']) == 2
    assert first['data'][0]['合同总金额'] == 1200000
    renders = [payload for event, payload in events if event == 'render_payload']
    assert [r['type'] for r in renders] == ['chart', 'action']
    assert renders[0]['data'][0] == {'name': '研发一部', '合同总金额': 1200000.0}
    assert all(event != 'tool_result' for event, _ in events)
    EVIDENCE['同轮多工具和双通道'] = {'决策请求': 2, '流式请求': 1, '工具执行': 2,
                                  '模型回填字段': sorted(first),
                                  '前端事件': [name for name, _ in events],
                                  '结构化结果': renders}


def verify_round_budget():
    replies = [response([tool_call('navigate_to_page', {'page_name': '合同查询'}, f'call-{n}-a'),
                         tool_call('navigate_to_page', {'page_name': '我的待办'}, f'call-{n}-b')]) for n in range(5)]
    requests, events = observe(replies)
    assert len(requests) == 6
    assert sum(name == 'tool_call' for name, _ in events) == 10
    assert requests[-1]['阶段'] == '流式' and not requests[-1]['携带工具定义']
    EVIDENCE['五轮限制'] = {'决策上限': 5, '本次工具执行': 10, '含最后生成的模型请求': 6,
                          '触顶后自动追加流式生成': True}


def verify_registry_and_user_boundary():
    names = {tool['function']['name'] for tool in tools.TOOLS}
    assert len(names) == 10 and names == set(tools._EXECUTORS)
    assert registry['ai_tools'] == {}
    assert list(inspect.signature(tools.execute_tool).parameters) == ['name', 'args']
    tree = ast.parse(inspect.getsource(chat.run_chat))
    assert not any(isinstance(node, ast.Name) and node.id == 'user' for node in ast.walk(tree))
    EVIDENCE['工具与授权接口'] = {'手工注册工具数': 10, '注册表中的工具数': 0,
                               '执行器参数': ['name', 'args'], '编排器使用user参数': False}


def verify_fallbacks():
    requests, events = observe([], configured=False)
    assert requests == [] and events[-1][0] == 'message_end'
    assert '尚未配置' in events[1][1]['content']
    assert '未知工具' in tools.execute_tool('unknown_tool', {})['text']
    invalid = tool_call('readonly_sql_query', {}, 'call-invalid')
    invalid['function']['arguments'] = '{invalid'
    requests, events = observe([response([invalid]), response()])
    tool_message = next(m for m in requests[-1]['messages'] if m['role'] == 'tool')
    assert json.loads(tool_message['content'])['text'] == 'SQL 为空'
    EVIDENCE['降级处理'] = {'未配置时模型请求': 0, '坏JSON参数被替换为': {},
                           '工具错误以普通结果回填': True}


def verify_sql_limits():
    try:
        query_readonly('SELECT * FROM sys_user')
    except ValueError as error:
        assert '白名单' in str(error)
    else:
        raise AssertionError('非白名单查询未被拒绝')
    conn = db.connect()
    try:
        conn.executemany('INSERT INTO contract (contract_no,contract_name,total_amount) VALUES (?,?,?)',
                         [(f'TEST-{n}', '仅用于分析的合成合同', 1) for n in range(220)])
        conn.commit()
    finally:
        conn.close()
    implicit = query_readonly('SELECT contract_no FROM contract')
    explicit = query_readonly('SELECT contract_no FROM contract LIMIT 205')
    assert len(implicit) == 200 and len(explicit) == 205
    EVIDENCE['SQL资源限制'] = {'无LIMIT时返回': len(implicit), '显式LIMIT205时返回': len(explicit),
                            '不存在统一200行硬上限': True}


def main():
    artifacts = ROOT / 'artifacts'
    artifacts.mkdir(exist_ok=True)
    original_path = db._db_path
    real_database = BACKEND / 'data/app.db'
    before = hashlib.sha256(real_database.read_bytes()).hexdigest()
    load_ontology(str(ROOT.parent / 'code-app-example/models'))
    with tempfile.TemporaryDirectory(prefix='harness-db-', dir=artifacts) as temporary:
        sandbox = Path(temporary).resolve()
        if not sandbox.is_relative_to(artifacts.resolve()):
            raise RuntimeError('临时数据库目录不在演示验证范围内。')
        db.init_db_path(str(sandbox / 'analysis.db'))
        try:
            conn = db.connect()
            conn.executescript((BACKEND/'schema.sql').read_text(encoding='utf-8'))
            conn.executescript("INSERT INTO department(id,department_no,department_name) VALUES (1,'TEST-01','研发一部'),(2,'TEST-02','研发二部'); INSERT INTO contract(contract_no,contract_name,total_amount,department_id) VALUES ('TEST-A','合成合同甲',1200000,1),('TEST-B','合成合同乙',800000,2);")
            conn.commit()
            conn.close()
            checks = [('文本历史与额外流式生成', verify_context_and_direct_reply),
                      ('真实SQL、工具顺序与双通道协议', verify_two_tools_and_protocols),
                      ('五轮决策不等于五个工具', verify_round_budget),
                      ('静态工具表与用户参数边界', verify_registry_and_user_boundary),
                      ('未配置及工具参数降级', verify_fallbacks),
                      ('SQL白名单与默认行数限制', verify_sql_limits)]
            for name, check in checks:
                check()
                print(f'通过：{name}')
        finally:
            db.init_db_path(original_path)
    assert hashlib.sha256(real_database.read_bytes()).hexdigest() == before, '原业务数据库发生变化'
    EVIDENCE['验证方式'] = {'真实编排器与工具': True, '模型返回': '模拟传输，不评价真实模型的选择质量',
                         '外部模型请求': 0, '业务数据库未变': True}
    (artifacts/'harness-evidence.json').write_text(json.dumps(EVIDENCE, ensure_ascii=False, indent=2), encoding='utf-8')
    print('六组编排观测全部通过，原业务数据库未变；证据已保存在忽略目录。')


if __name__ == '__main__':
    main()

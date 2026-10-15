/* === 轻量编排的教学回放：状态来自已核验的真实调用顺序 === */
const HARNESS_STEPS = [
  {
    title: '准备消息与开始事件', requests: 0, tools: 0,
    protocol: 'system + 最近 10 条文本 + 当前问题\nSSE: message_start',
    explanation: '上下文由控制代码组装。本轮工具轨迹从空白开始，随后写入同一个 messages 列表。',
  },
  {
    title: '第一次决策，返回两个工具', requests: 1, tools: 0,
    protocol: 'stream: false\ntools: 10 个 schema，tool_choice: auto\nassistant.tool_calls = [SQL, 导航]',
    explanation: '模型给出工具名称和参数。控制层先保存 assistant 的工具请求，再负责真正调用本地函数。',
  },
  {
    title: '执行 SQL，并回填第一个结果', requests: 1, tools: 1,
    protocol: 'execute_tool("readonly_sql_query", args)\nmessages += role: tool, tool_call_id: "call-sql"\nSSE: tool_call → render_payload(chart)',
    explanation: '查询数据进入模型上下文；图表协议单独推送给前端。执行工具本身没有新增模型请求。',
  },
  {
    title: '同一轮继续执行导航工具', requests: 1, tools: 2,
    protocol: 'execute_tool("navigate_to_page", args)\nmessages += role: tool, tool_call_id: "call-navigation"\nSSE: tool_call → render_payload(action)',
    explanation: '第二个工具按返回顺序执行，不与 SQL 并行。工具只返回导航按钮，等待用户点击。',
  },
  {
    title: '第二次决策，没有工具调用', requests: 2, tools: 2,
    protocol: 'stream: false，继续携带 tools\n返回 message，但 tool_calls 为空\nbreak',
    explanation: '这个非流式回答未追加到 messages，也未直接展示；循环结束后还会进行一次生成。',
  },
  {
    title: '第三次请求，重新流式生成', requests: 3, tools: 2,
    protocol: 'stream: true\n本次请求不携带 tools\nSSE: delta → delta → …',
    explanation: '流式客户端只读取文本增量。模型基于系统语义、历史和本轮工具结果，重新生成最终回答。',
  },
  {
    title: '结束，并记录请求级审计', requests: 3, tools: 2,
    protocol: 'SSE: message_end\nHTTP 路由 finally:\nwrite_audit("AI_CHAT", question[:200])',
    explanation: '前端结束发送中的状态；后端记录本次提问。当前没有逐工具的参数、结果与耗时审计。',
  },
];

class HarnessTrace {
  constructor(root) {
    this.root = root;
    this.index = 0;
    this.next = root.querySelector('#harnessNext');
    this.previous = root.querySelector('#harnessPrevious');
    this.next.addEventListener('click', () => this.show(this.index + 1));
    this.previous.addEventListener('click', () => this.show(this.index - 1));
    root.querySelector('#harnessReset').addEventListener('click', () => this.show(0));
    this.show(0);
  }

  show(index) {
    this.index = Math.max(0, Math.min(index, HARNESS_STEPS.length - 1));
    const step = HARNESS_STEPS[this.index];
    this.root.querySelector('#harnessRequestCount').textContent = step.requests;
    this.root.querySelector('#harnessToolCount').textContent = step.tools;
    this.root.querySelector('#harnessStepTitle').textContent = step.title;
    this.root.querySelector('#harnessProtocol').textContent = step.protocol;
    this.root.querySelector('#harnessExplanation').textContent = step.explanation;
    for (const node of this.root.querySelectorAll('[data-trace-step]')) {
      const position = Number(node.dataset.traceStep);
      node.classList.toggle('current', position === this.index);
      node.classList.toggle('completed', position < this.index);
    }
    this.next.disabled = this.index === HARNESS_STEPS.length - 1;
    this.previous.disabled = this.index === 0;
  }
}

const harnessTraceRoot = document.getElementById('harnessTrace');
if (harnessTraceRoot) new HarnessTrace(harnessTraceRoot);

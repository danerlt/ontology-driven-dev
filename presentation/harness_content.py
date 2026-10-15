"""AI 对话的五页深讲；结论由真实编排器观测与源码共同支持。"""


def create_harness_slides(slide, backend):
    frontend = 'code-app-example/frontend/src/'
    return [
        slide('轻量 harness：模型外的那层控制代码',
              '本 demo 用一段决策循环、一个函数分发表和一套流协议，把模型接进业务系统。', '''
          <div class="harness-structure" data-check="轻量编排职责图">
            <div class="blue-surface harness-thesis"><h3>模型选择工具<br>代码推进执行</h3><p>何时请求模型、执行哪个函数、<br>把什么结果放回上下文，<br>由控制层明确决定。</p><div class="divider"></div><p class="small">核心入口：<code>run_chat()</code><br>通过 <code>yield (event, payload)</code><br>向 HTTP 层逐步产出事件。</p></div>
            <table class="data-table harness-files"><thead><tr><th>位置</th><th>承担的控制职责</th></tr></thead><tbody>
              <tr><td><code>AIChat.tsx</code></td><td>维护文本历史、禁止重复发送、接收结果</td></tr>
              <tr><td><code>api/ai.py</code></td><td>登录入口、SSE 编码、请求级审计</td></tr>
              <tr><td><code>ai/chat.py</code></td><td>组装消息、循环决策、回填结果、结束生成</td></tr>
              <tr><td><code>ai/tools.py</code></td><td>注册 10 个工具，按名称分发到本地函数</td></tr>
              <tr><td><code>ai/llm.py</code></td><td>用 requests 调用模型的兼容接口</td></tr>
            </tbody></table>
          </div>''',
              '''这里把 harness 理解为包在模型外、负责控制执行过程的应用代码。这是对本 demo 实现结构的归纳。
模型返回工具名和参数，但不会直接执行 Python 或 SQL。chat.py 的 run_chat 负责消息序列、循环、调用工具和结束条件；tools.py 的分发表决定具体执行哪个本地函数。模型 HTTP 传输由 llm.py 使用 requests 完成。
外围还有两层：浏览器组件保存显示中的对话，HTTP 路由负责登录校验、SSE 封装及结束后的审计。控制状态分散在这些清晰的小模块里，没有额外的 Agent 框架负责调度。
工具参数的 JSON 解析失败会转为空参数，执行器未做独立的 JSON Schema 校验。未知工具或函数异常转成普通工具结果回填；是否再次尝试仍由后续模型决策决定。
因此，理解它应该从一次请求如何推进开始，而不是只看 system prompt。接下来的五页属于可选深讲，约增加六到八分钟。''',
              [backend+'ai/chat.py', backend+'ai/tools.py', backend+'ai/llm.py', backend+'api/ai.py', frontend+'components/AIChat.tsx'],
              chapter='AI 深讲', footer='轻量 harness · 模型外的控制职责', topic='harness-structure'),

        slide('上下文分三层，记忆只保留文本',
              '系统语义每次重建；历史由浏览器回传；工具轨迹只在本次请求中追加。', '''
          <div class="two harness-context" data-check="编排上下文生命周期">
            <div><table class="data-table"><thead><tr><th>消息层</th><th>真实来源与生命周期</th></tr></thead><tbody>
              <tr><td><b>system</b></td><td>业务背景 + 注册表语义<br>+ API 能力 + 表结构 + 行为准则</td></tr>
              <tr><td><b>历史文本</b></td><td>前端 messages → 最近 10 条<br>后端再筛选 user / assistant</td></tr>
              <tr><td><b>本轮轨迹</b></td><td>追加当前 user、assistant 工具请求<br>以及 role=tool 的执行结果</td></tr>
            </tbody></table><p class="source-caption">实际提示词投影对象、行为、规则和流程；并未完整注入七模型的全部细节。</p></div>
            <div class="blue-surface"><h3 class="harness-memory-title">最近 10 条<br>不是最近 10 轮</h3><p class="text">下一次提问回传的是文本。<br>原始工具结果、图表卡片<br>和工具调用 ID 不随历史回传。</p><div class="divider"></div><p class="small">当前没有会话落库、历史摘要<br>和基于 token 的输入裁剪逻辑。</p></div>
          </div>''',
              '''前端先对 messages 过滤空文本，再取最后十条，映射成 user 或 assistant。随后才追加当前用户问题和空的 AI 占位消息，所以不会把本轮用户问题重复放进 history。
后端每次重新调用 build_system_prompt，再从 history 的最后十条里筛选合法文本角色，最后追加当前 user。十四条正常历史的隔离观测中，模型首个请求收到 system、十条历史和当前问题，共十二条消息。
工具调用请求和工具结果会在这一次 run_chat 的 messages 列表里累积，但前端只保存最终文字及渲染卡片；下次发送 history 时只映射文字，不回传原始数据、卡片和工具调用 ID。文字回答里可能仍含数据摘要，不能等同于完全遗忘结果。
规范提出过会话持久化与摘要压缩，当前 demo 没有落实这些机制。max_tokens 是传给模型的输出参数，并没有在代码中承担输入上下文预算管理。''',
              [frontend+'components/AIChat.tsx', frontend+'api/ai.ts', backend+'ai/chat.py', backend+'ai/prompt.py', 'references/AI 原生应用技术架构设计文档.md'],
              chapter='AI 深讲', footer='上下文构造 · 历史文本与本轮轨迹', topic='harness-context'),

        slide('一次提问，怎样走完工具循环',
              '教学回放：模型在同一轮要求统计数据并定位页面；两个工具按返回顺序执行。', '''
          <div class="harness-trace" id="harnessTrace" data-check="编排逐步回放">
            <div class="harness-timeline" aria-label="编排步骤">
              <div class="harness-step current" data-trace-step="0"><span>0</span><p>准备消息与开始事件</p></div>
              <div class="harness-step" data-trace-step="1"><span>1</span><p>模型返回两个工具调用</p></div>
              <div class="harness-step" data-trace-step="2"><span>2</span><p>执行只读 SQL，返回图表</p></div>
              <div class="harness-step" data-trace-step="3"><span>3</span><p>执行导航，返回页面按钮</p></div>
              <div class="harness-step" data-trace-step="4"><span>4</span><p>再次决策，发现无需工具</p></div>
              <div class="harness-step" data-trace-step="5"><span>5</span><p>另发流式请求，生成答案</p></div>
              <div class="harness-step" data-trace-step="6"><span>6</span><p>结束事件与请求级审计</p></div>
            </div>
            <div class="harness-trace-card"><div class="harness-trace-metrics"><span>模型请求 <b id="harnessRequestCount">0</b> 次</span><span>工具执行 <b id="harnessToolCount">0</b> 次</span></div><h3 id="harnessStepTitle">准备上下文</h3><pre id="harnessProtocol" aria-live="polite"></pre><p id="harnessExplanation" aria-live="polite"></p><div class="harness-trace-actions"><button class="action-button" id="harnessNext">回放下一步</button><button class="secondary-button" id="harnessPrevious">回放上一步</button><button class="secondary-button" id="harnessReset">重置编排回放</button></div></div>
          </div>''',
              '''这条回放对应真实编排代码的一个受控场景，模型返回由测试传输模拟，SQL 工具和本地函数分发则运行真实实现；演示按钮本身不连接模型或业务库。
第一步调用非流式 chat_completion，携带十个工具 schema，tool_choice 为 auto。模型一次返回 SQL 和导航两个 tool_calls。控制层先将这条 assistant 消息追加到 messages，再顺序执行两个工具；每个结果都用对应 tool_call_id 作为 role=tool 消息回填。
第二次决策没有 tool_calls，循环直接 break。这个非流式回答没有追加进 messages，也没有直接展示。代码随后另外调用不带 tools 的 stream_chat_completion，由它基于已有上下文重新生成文字。因此该场景共有三次模型请求、两次工具执行。
MAX_TOOL_ROUNDS=5 限制的是决策请求轮数，每轮可以有多个工具。另一个隔离观测连续五轮各返回两个工具，实际执行十次工具后仍进入第六次模型请求，强制流式收尾。''',
              [backend+'ai/chat.py', backend+'ai/llm.py', backend+'ai/tools.py', backend+'api/ai.py'],
              chapter='AI 深讲', footer='教学回放 · 两次决策 + 一次流式生成', topic='harness-loop'),

        slide('同一工具结果，走两条不同通道',
              '工具函数返回 text、data、render；模型读业务结果，前端读展示协议。', '''
          <div class="harness-tool-strip" data-check="工具执行管线"><code>TOOLS</code><span>→ 名称匹配 →</span><code>_EXECUTORS</code><span>→ 本地服务 / SQL →</span><code>{ text, data, render }</code></div>
          <div class="two harness-protocols" data-check="模型与前端双通道">
            <article class="surface"><span class="tag">回填给模型</span><h3>role = tool</h3><pre>tool_call_id: "call-sql"
content: JSON({ text, data })</pre><p>与原 tool_calls 的 ID 对应，<br>供下一轮决策和最终回答使用。</p></article>
            <article class="surface"><span class="tag">推送给界面</span><h3>event = render_payload</h3><pre>{ type: "chart",
  chart_type: "bar", data: [...] }</pre><p>POST fetch 读取 SSE 字节流，<br>回调分发给表格、ECharts 和导航按钮。</p></article>
          </div>
          <p class="source-caption">工具 schema 与分发表均为手工维护；本实现没有单独发送 tool_result 这一 SSE 事件。</p>''',
              '''tools.py 的 TOOLS 是十个手工定义的函数 schema，_EXECUTORS 是工具名到本地函数的映射。execute_tool 只接受 name 和 args；本体注册表里的 ai_tools 在当前加载器中仍为空，不能把这里讲成 YAML 自动注册工具。
函数结果中的 text 和 data 会序列化给模型，render 则单独通过 render_payload 发给前端。图表数据的转换由 Python 工具函数确定，前端按 type、chart_type 等字段渲染，而不是让浏览器执行模型生成的 HTML 或 JavaScript。
前端使用 POST fetch，带登录令牌并读取 ReadableStream，通过 TextDecoder 和换行缓冲解析 event/data，再调用 onDelta、onRender、onToolCall、onDone。这里不是浏览器原生 EventSource。
实际工具状态事件只包含工具名，没有完整参数；工具结果也没有独立的 tool_result 事件。导航返回的是一个用户可点击按钮，不会直接替用户提交或审批。''',
              [backend+'ai/tools.py', backend+'ai/chat.py', backend+'api/ai.py', frontend+'api/ai.ts', frontend+'components/AIChat.tsx', backend+'ontology/registry.py'],
              chapter='AI 深讲', footer='工具协议 · 模型上下文与前端渲染各有通道', topic='harness-protocol'),

        slide('轻在哪里，边界就要讲在哪里',
              '已有控制形成了可运行闭环；更完整的状态、预算、权限与观测仍需补齐。', '''
          <table class="data-table harness-boundaries" data-check="编排已有控制与边界"><thead><tr><th>控制面</th><th>当前已经实现</th><th>当前尚未覆盖</th></tr></thead><tbody>
            <tr><td><b>状态</b></td><td>本轮消息列表；最近 10 条历史文本</td><td>会话落库、摘要、断点恢复与原始工具记忆</td></tr>
            <tr><td><b>执行</b></td><td>5 轮决策；工具顺序执行；HTTP timeout=120</td><td>总工具次数、费用与总时限预算、取消传播</td></tr>
            <tr><td><b>授权</b></td><td>对话入口登录；工具表只提供读取与导航</td><td>按用户裁剪工具、逐工具及行级策略</td></tr>
            <tr><td><b>SQL</b></td><td>SELECT 检查、表白名单、缺省 LIMIT 200</td><td>统一行数硬上限、SQL 执行超时与只读连接</td></tr>
            <tr><td><b>观测</b></td><td>异常转文本；记录 AI_CHAT 与问题前 200 字</td><td>每次工具的参数、结果、耗时和失败轨迹审计</td></tr>
          </tbody></table>
          <div class="harness-boundary-note" data-check="编排限制结论">控制强度由代码中的真实检查决定；提示词的“只读要求”仍需执行层约束配合。</div>''',
              '''这页帮助同事判断“轻量”到底轻在什么地方。它已经有固定工具集、执行循环、结果回填、流式输出和请求级异常处理，足以展示应用内 AI 查询闭环。
但五轮循环并没有统一的费用或总时限预算。工具失败会被包装成普通结果回填，模型下一轮可能再尝试，但控制层没有独立重试策略；前端也没有取消按钮或 AbortController。requests 的 timeout=120 不能作为整条对话总时限来理解。
授权方面，API 入口有登录校验，但 run_chat 的 user 参数没有用于编排，工具执行器也不接收 user；当前未见按用户裁剪工具或注入行级范围。这里限定在所分析的 AI 调用链，不扩大成全系统权限审计结论。
SQL 的 200 行是缺省追加，显式 LIMIT 205 在临时库观测中确实返回了 205 行；函数注释里的执行超时和严格上限不能当作实现证据。API finally 中只记录 AI_CHAT 和用户问题前两百字，尚无每次工具的细粒度轨迹。''',
              [backend+'ai/chat.py', backend+'ai/llm.py', backend+'ai/tools.py', backend+'sql_readonly/query.py', backend+'api/ai.py', frontend+'api/ai.ts', frontend+'components/AIChat.tsx'],
              chapter='AI 深讲', footer='边界依据 · 对照实现与六组隔离观测', topic='harness-boundaries'),
    ]

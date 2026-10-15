"""分享内容与讲解备注；所有业务结论均可追溯到仓库。"""

FRAMEWORK = 'references/ontology_modeling_framework_v9.md'
GUIDE = 'references/本体模型业务功能开发指导书.md'
REQUIREMENTS = 'references/AI需求探索与确认提示词V9.0.md'
MODELS = 'code-app-example/models/'
BACKEND = 'code-app-example/backend/'


def slide(title, lead, body, notes, sources, chapter='原理', footer='销售合同执行管理案例', kind='', topic=''):
    return dict(title=title, lead=lead, body=body, notes=notes, sources=sources,
                chapter=chapter, footer=footer, kind=kind, topic=topic)


SLIDES = [
    slide('把业务共识变成系统的骨架', '', '''
      <h1 data-edit="cover-title" data-check="封面标题">把业务共识<br>变成系统的骨架</h1>
      <p class="intro" data-edit="cover-intro" data-check="封面简介">从一笔销售合同出发，理解需求、七模型与可运行应用之间的关系。</p>
      <div class="pipeline" data-check="三阶段主线">需求探索　→　本体建模　→　应用构建</div>
      <div class="cover-meta">本体驱动开发　／　原理与工程实践</div>
      <div class="cover-graph" aria-label="七模型构成的业务语义关系图">
        <svg viewBox="0 0 740 675" aria-hidden="true"><g fill="none" stroke="#4361ee" stroke-width="2" opacity=".3"><path d="M160 85 L480 85 L640 325 L480 565 L160 565 L0 325 Z"/><path d="M160 85 L320 325 L480 85 M640 325 L320 325 L480 565 M160 565 L320 325 L0 325"/></g></svg>
        <div class="graph-node" style="left:80px;top:27px"><b>M1</b><span>对象</span></div>
        <div class="graph-node" style="left:400px;top:27px"><b>M2</b><span>行为</span></div>
        <div class="graph-node" style="left:560px;top:267px"><b>M3</b><span>规则</span></div>
        <div class="graph-node" style="left:400px;top:507px"><b>M5</b><span>主体</span></div>
        <div class="graph-node" style="left:80px;top:507px"><b>M6</b><span>流程</span></div>
        <div class="graph-node" style="left:-80px;top:267px"><b>M7</b><span>报表</span></div>
        <div class="graph-node graph-center" style="left:240px;top:267px"><b>MU</b><span>界面入口</span></div>
      </div>''',
      '''今天要回答的核心问题是：怎样让 AI 写出来的业务系统，仍然能被人理解、验证和持续维护？
我们不从 YAML 语法开始，而是从一笔销售合同出发，顺着合同登记、审批、开票、收款，看到需求如何成为模型，模型又怎样约束代码。
这是一场约二十分钟的研发分享。前半段建立七模型的分工，后半段用真实代码和两个交互示例解释运行机制。按 N 可以看到当前页讲稿和源码依据。''',
      ['README.md', 'SKILL.md', FRAMEWORK], chapter='开场', footer='主线约 20 分钟 · AI 深讲可选', kind='cover'),

    slide('难点，是让三份答案始终一致', '同一条业务规则，往往同时存在于需求、模型和代码中。', '''
      <div class="drift" data-check="语义漂移对照">
        <article><span class="tag">需求</span><h3>业务怎么说</h3><p>“大额合同需要总经理审批。”<br>大额是多少？谁负责审批？</p></article>
        <article><span class="tag">模型</span><h3>系统怎么理解</h3><p>金额 ≥ 100 万元时，<br>进入总经理审批节点。</p></article>
        <article><span class="tag">代码</span><h3>实际怎么执行</h3><p>条件、权限、状态与页面，<br>都必须落实同一条规则。</p></article>
        <span class="broken" style="left:510px">↔</span><span class="broken" style="left:1115px">↔</span>
      </div>
      <div class="takeaway" data-edit="drift-takeaway" data-check="问题结论">本体驱动开发要建立一条可追溯的语义链，减少“模型一套、代码一套”。</div>''',
      '''可以先让同事想一下：最近一次改审批规则，改了多少地方？需求文档、后端判断、流程配置、前端提示，可能都有这条规则的影子。
问题不只是能否生成代码，而是同一业务含义能否在不同产物中保持一致。在这个样例中，金额达到一百万元需要总经理审批，这是业务事实；模型引用、流程节点和实际实现应该都围绕这个事实组织。
这里的“减少漂移”是方法论目标，不能据此宣称仓库已经自动验证了所有一致性。后面会明确区分规范门禁和实际代码。''',
      ['SKILL.md', MODELS+'m3-rule-model.yaml', MODELS+'m6-flow-model.yaml']),

    slide('这里的“本体”，是一套业务语义契约', '把业务世界拆成职责清晰、可互相引用的模型元素。', '''
      <div class="two" data-check="本体定义">
        <div>
          <p class="big-statement" data-edit="ontology-definition">对象是什么，<br>谁能做什么，<br>何时允许、如何协作。</p>
          <div class="source-caption">本项目采用面向业务软件的七模型 YAML 方案。</div>
        </div>
        <div class="blue-surface">
          <h3 class="subhead">用稳定 ID 连接业务含义</h3>
          <p class="text">“录入收款” → <code>Receipt_Record</code><br>“收款权限” → <code>PERM-RECEIPT-RECORD</code></p>
          <div class="divider"></div>
          <p class="text">界面引用行为，行为引用规则，<br>流程引用角色与行为。</p>
          <p class="small muted" style="margin-top:27px">同一个业务事实，只有一个定义位置。</p>
        </div>
      </div>''',
      '''这里需要先限定“本体”的语境：我们讨论的是仓库自己的业务软件建模方案，使用 YAML 表达对象、行为、规则等语义。理解这个项目，并不需要先学习 OWL、RDF 或知识图谱推理。
它借鉴了领域模型、聚合和状态机等思想，但又把权限、流程、报表和界面入口纳入统一的引用体系。重点是分工和连接：规则定义一次，行为按 ID 引用；流程引用行为，而不是把行为内容抄一遍。
因此，YAML 的价值不在于格式本身，而在于结构化的定义、稳定的标识，以及可以检查的引用关系。''',
      [FRAMEWORK, MODELS+'m2-behavior-model.yaml', MODELS+'m5-actor-model.yaml']),

    slide('三阶段，把不确定性逐步收敛', '先确认业务，再建立模型，最后落实到可运行系统。', '''
      <div class="flow-three" data-check="三阶段管线">
        <article><span class="outline-no">01</span><h3>需求探索</h3><p>总体理解、对象、功能规则、联动、流程、报表、权限与可选原型。</p><div class="output">需求规格说明书<br>附录 C：建模输入基线</div></article>
        <div class="arrow">→</div>
        <article><span class="outline-no">02</span><h3>本体建模</h3><p>形成七模型及稳定 ID，校核引用、覆盖关系与模型一致性。</p><div class="output">7 份 YAML<br>+ manifest.json</div></article>
        <div class="arrow">→</div>
        <article><span class="outline-no">03</span><h3>应用构建</h3><p>复制技术底座，落实业务服务、流程、界面和运行时 AI。</p><div class="output">可运行的<br>浏览器前后端系统</div></article>
      </div>
      <div class="gate" data-check="需求确认纪律"><b>规范要求</b><span>需求探索阶段逐步人工确认；企业专属规则不能由 AI 自行定案。</span></div>''',
      '''第一阶段不是立即写代码，而是把业务边界、对象、规则和协作方式问清楚。行业通用的内容允许 AI 补全；企业专属的审批阈值、角色职责和规则必须由人确认。根技能要求需求探索内部按阶段确认。
第二阶段以需求说明书附录 C 为确定性输入，输出七份 YAML 和清单。此时要避免重新猜测业务。
第三阶段复制 Python 或 Go 技术底座，再依据模型扩展成业务应用。模型是约束来源，具体服务、页面、接口与集成仍要实现和验证。
这条管线可以分段进入，已有需求文档可以只建模，已有模型也可以直接构建。''',
      ['SKILL.md', REQUIREMENTS, GUIDE], footer='需求探索 → 本体建模 → 应用构建'),

    slide('七模型，回答七类不同的问题', '点击模型，查看它的职责、边界与样例中的真实 ID。', '''
      <div class="model-layout" data-check="七模型职责">
        <div class="model-grid">
          <button class="model-button selected" data-model="M1" aria-label="M1 对象模型" aria-pressed="true"><b>M1</b><span>对象</span></button>
          <button class="model-button" data-model="M2" aria-label="M2 行为模型" aria-pressed="false"><b>M2</b><span>行为</span></button>
          <button class="model-button" data-model="M3" aria-label="M3 规则模型" aria-pressed="false"><b>M3</b><span>规则</span></button>
          <button class="model-button" data-model="M5" aria-label="M5 主体模型" aria-pressed="false"><b>M5</b><span>主体</span></button>
          <button class="model-button" data-model="M6" aria-label="M6 流程模型" aria-pressed="false"><b>M6</b><span>流程</span></button>
          <button class="model-button" data-model="M7" aria-label="M7 查询报表模型" aria-pressed="false"><b>M7</b><span>查询报表</span></button>
          <button class="model-button" data-model="MU" aria-label="MU 界面模型" aria-pressed="false"><b>MU</b><span>界面</span></button>
          <p class="model-hint">编号沿用历史体系。<br>V9 保留这七类模型，<br>因此没有 M4。</p>
        </div>
        <div class="model-detail" id="modelDetail" aria-live="polite"></div>
      </div>''',
      '''这一页可以作为整个分享的导航图。建议依次点击 M1、M2、M3，再快速带过 M5、M6、M7 和 MU。
M1 定义业务对象；M2 负责改变状态的行为；M3 负责独立复用的判断；M5 定义角色和权限；M6 表达多角色、多步骤的协作；M7 组织读取的数据；MU 负责用户入口和界面追溯。
模型编号不连续是历史沿用，不是漏了一个模型。V9 取消了旧体系中的事件、场景、对象数据表映射和接口等独立模型，当前主线面向单体同步业务系统。
图上的排列仅用于选择职责，不代表真实模型依赖方向。''',
      [FRAMEWORK, MODELS+'manifest.json'], footer='M1 · M2 · M3 · M5 · M6 · M7 · MU'),

    slide('M1：先找到业务边界，再考虑数据表', '合同与付款阶段属于同一聚合；开票和收款独立存在。', '''
      <div class="aggregate-layout" data-check="聚合与关联">
        <div>
          <div class="aggregate"><div class="aggregate-title"><h3>合同</h3><span class="tag">聚合根</span></div><p class="small muted" style="margin-top:14px">AGG-CONTRACT-001 · Contract</p><div class="entity"><h4>付款阶段明细</h4><p>金额、比例、约定日期、开票状态<br>依附合同生命周期，由合同入口维护</p></div></div>
          <div class="relations"><span class="mini-object">开票</span><span>通过 ID 关联</span><span class="mini-object">收款</span></div>
          <p class="source-caption">持久化可以拆成主表、从表，但业务入口和一致性边界仍由聚合表达。</p>
        </div>
        <div><div class="boundary-line"><strong>生命周期</strong><p>哪些数据必须同生共死？</p></div><div class="boundary-line"><strong>不变性</strong><p>哪些约束必须在一次行为内满足？</p></div><div class="boundary-line"><strong>对外入口</strong><p>外部通过聚合根操作，避免任意修改明细。</p></div></div>
      </div>''',
      '''从数据库出发，很容易把每张表当成一个独立业务对象。M1 反过来，先问业务完整性和生命周期。
合同头和付款阶段明细共同构成一个合同聚合。付款阶段不能脱离合同独立存在，维护时应由合同这个入口统一检查，比如付款比例合计等于百分之百。
开票和收款则有独立的状态和生命周期，所以是其他聚合，通过 ID 关联合同。最终数据库可以把合同和付款阶段存成两张表，但两张表并不自动意味着两个聚合。
这是逻辑职责的边界。样例的一条同步链会把多个聚合的写操作放进同一个数据库事务，后面单独解释。''',
      [FRAMEWORK, MODELS+'m1-object-model.yaml', BACKEND+'services/contract_service.py']),

    slide('M2 与 M3：动作和判断，各管一件事', '行为改变状态，规则判断条件；联动关系显式声明。', '''
      <div class="two" data-check="行为规则分工">
        <div><div class="concept-heading"><span class="tag">M2 行为</span><b>录入收款</b></div><div class="codebox" style="height:430px"><div class="filename">真实模型节选 · 省略部分字段</div><pre><span class="code-accent">id: Receipt_Record</span>
ownerEntity: AGG-RECEIPT-001
appliedRules:
  - RULE-INVOICE-REMAIN-RECEIPT-QUOTA
syncTriggers:
  - behaviorRef:
      Invoice_UpdateReceiptStatus</pre></div></div>
        <div><div class="concept-heading"><span class="tag">M3 规则</span><b>检查剩余额度</b></div><p class="big-statement" style="font-size:43px;margin:38px 0">累计有效收款<br>+ 本次收款<br>≤ 开票金额</p><div class="takeaway">规则拒绝超额收款；<br>行为负责登记并更新状态。</div></div>
      </div>''',
      '''用录入收款来区分行为和规则。Receipt_Record 回答的是：记录了什么，以及状态变成什么。剩余额度规则回答的是：这次金额是否允许。
把规则单独表达的价值在于复用与追溯。审批、开票或其他入口需要相同判断时，可以引用同一条业务含义。
展示的 YAML 来自样例，做了字段省略和排版简化。实际样例还检查开票必须已批准、收款合同必须与开票合同一致、金额必须大于零。
特别注意：当前样例的领域规则主要由 Python 函数实现，并非每一条表达式都交给通用规则引擎动态解释。模型与实现的关系是语义对齐。''',
      [MODELS+'m2-behavior-model.yaml', MODELS+'m3-rule-model.yaml', BACKEND+'services/domain_rules.py']),

    slide('一笔收款，沿稳定 ID 追到真实代码', '从界面入口出发，能回答“调用什么、检查什么、改动什么”。', '''
      <div class="two" style="grid-template-columns:1.15fr .85fr" data-check="收款追溯链">
        <div class="trace-list">
          <div class="trace-item"><b>MU 操作</b><div><code>frmReceiptMaintain / actSave</code><small>保存操作引用 Receipt_Record</small></div></div>
          <div class="trace-item"><b>M5 授权</b><div><code>PERM-RECEIPT-RECORD</code><small>接口检查当前用户的收款登记权限</small></div></div>
          <div class="trace-item"><b>M2 行为</b><div><code>Receipt_Record</code><small>M3 校验 + 收款状态 + syncTriggers</small></div></div>
          <div class="trace-item"><b>代码入口</b><div><code>POST /api/receipt</code><small>receipt_service.record(data, user)</small></div></div>
        </div>
        <div class="trace-result"><h3>追溯是一种<br>工程检查能力</h3><p>接口实现了模型语义，<br>不要求函数名与行为 ID<br>逐字相同。</p><div class="divider"></div><p style="font-size:25px">修改业务规则时，能找全受影响的模型、接口、服务与测试。</p></div>
      </div>''',
      '''这一页逐层读下来。MU 的收款界面中，保存操作引用 Receipt_Record，同时绑定收款登记权限。M5 定义权限和目标行为。
实际后端入口是 POST /api/receipt。路由先登录校验，再检查 PERM-RECEIPT-RECORD，之后进入 receipt_service.record。
这说明行为 ID 是跨产物的语义标识，不等于必须存在一个同名 Python 函数，也不等于所有请求都由一个行为解释器派发。
团队做代码评审时，可以反向检查：这个接口对应哪个行为，行为对应哪条需求，权限和规则是否都落实；也可以正向检查模型有没有遗漏实现。''',
      [MODELS+'mu-ui-model.yaml', MODELS+'m5-actor-model.yaml', BACKEND+'api/receipt.py', BACKEND+'services/receipt_service.py'], chapter='案例'),

    slide('同步联动，把跨对象协作写清楚', 'V9 主线通过 syncTriggers 与流程编排实现协作。', '''
      <div class="sync-flow" data-check="收款同步链">
        <div class="sync-box"><h3>登记 / 冲销收款</h3><code>Receipt_Record<br>Receipt_Reverse</code></div><div class="arrow">→</div>
        <div class="sync-box"><h3>重算开票收款状态</h3><code>Invoice_<br>UpdateReceiptStatus</code></div><div class="arrow">→</div>
        <div class="sync-box decision"><h3>判断并更新合同结清</h3><code>RULE-CONTRACT-SETTLEMENT<br>↓<br>Contract_UpdateSettlementStatus</code></div>
      </div>
      <p class="rule-equation" data-check="结清条件"><span>全部付款阶段足额开票</span>　且　<span>全部有效开票收齐</span></p>
      <div class="transaction-band" data-check="样例事务边界"><b>样例实现</b><span>显式调用同步服务，共用 conn；成功后统一提交，异常则回滚。</span></div>
      <p class="source-caption">单个行为承担一个聚合的职责；样例的整条同步写入链共用数据库事务。</p>''',
      '''先看业务模型：收款登记和冲销都同步触发开票收款状态重算；重算后，根据合同结清资格规则调用合同状态更新行为。
再看代码：receipt_service 的事务回调把同一个 conn 传给 sync_service。收款、开票累计金额、合同结清状态的写入最终由 db.transaction 统一提交，异常回滚。
这里有一个需要明确的口径：文档一处强调聚合事务边界，另一处又描述整条同步编排共用事务。讲解时应以真实实现限定结论——本样例确实让跨聚合同步链共用连接，而不能把它说成通用的分布式事务方案。
此外，部分规则校验在事务回调之前执行，并发一致性仍需要专项评估。''',
      [FRAMEWORK, BACKEND+'services/receipt_service.py', BACKEND+'services/sync_service.py', BACKEND+'db.py'], chapter='案例'),

    slide('现场试一下：收齐，不一定就结清', '教学模拟：一张 100 万元的已批准开票，已有效收款 40 万元。', '''
      <div class="simulation" data-check="收款联动模拟">
        <div class="sim-controls"><label for="receiptAmount">本次收款金额</label><div class="amount-input"><input id="receiptAmount" type="number" min="0.01" max="100" step="0.01" value="60"><span>万元</span></div><div class="row"><button class="action-button" id="recordReceipt">登记模拟收款</button><button class="secondary-button" id="reverseReceipt">冲销最近一笔</button></div><label class="check-label"><input type="checkbox" id="stagesFullyInvoiced" checked>所有付款阶段均已足额开票</label><div id="receiptMessage" role="status"></div><button class="secondary-button" id="resetReceipt" style="font-size:22px;padding:10px 18px">重置示例</button></div>
        <div class="sim-result"><div class="metric-header"><span>累计有效收款</span><span>开票金额 100 万元</span></div><div class="metric-amount"><span id="receivedValue">40</span> <small>万元</small></div><div class="progress-track"><div class="progress-value" id="receiptBar"></div></div><div class="status-row"><span>开票收款状态</span><b id="invoiceState">未全部收齐</b></div><div class="status-row"><span>合同状态</span><b id="contractState">已纳入管理</b></div><p class="sim-note">先补收 60 万，再冲销；也可以取消左侧勾选，观察“收齐”和“结清”的差别。</p></div>
      </div>''',
      '''这一页建议现场操作，约花一到两分钟。
先登记六十万元，观察开票变成已全部收齐，合同变成已结清。再冲销最近一笔，累计收款回到四十万元，合同恢复已纳入管理。
接着取消“所有付款阶段均已足额开票”，再收六十万元。现在开票已经收齐，但合同仍然不结清，因为另一半条件不满足。最后可以输入六十一万元，展示额度规则拒绝操作，状态保持不变。
这只是前端教学模拟：设定合同只有当前这一张有效开票，且合同处于可结清状态。它没有连接真实后端，也不模拟完整业务数据和并发事务。''',
      [MODELS+'m3-rule-model.yaml', BACKEND+'services/domain_rules.py', BACKEND+'services/sync_service.py'], chapter='案例', footer='教学模拟 · 页面本地状态 · 单位：万元'),

    slide('M5 与 M6：角色决定谁做，流程决定顺序', '合同先经过财务经理；金额达到 100 万元时，再经过总经理。', '''
      <div class="approval-layout" data-check="审批分支演示">
        <div class="sim-controls"><label for="contractAmount">合同金额</label><div class="amount-input"><input id="contractAmount" type="number" min="1" value="120" step="1"><span>万元</span></div><div class="divider"></div><p class="text">M3 判断金额条件<br>M5 定义审批角色<br>M6 组织任务与分支</p></div>
        <div class="approval-route"><div class="route-track"><div class="route-node"><h3>财务经理</h3><p>先审批</p></div><div class="arrow">→</div><div class="route-node" id="gmStep" data-enabled="true"><h3>总经理</h3><p>金额 ≥ 100 万</p></div><div class="arrow">→</div><div class="route-node"><h3>纳入管理</h3><p>审批通过</p></div></div><div class="approval-rule" id="approvalDecision" role="status"></div><p class="small muted">流程节点引用角色 ID，不直接写某位同事姓名。<br>规则判断、任务分配与行为执行各自有明确归属。</p></div>
      </div>''',
      '''把金额从一百二十改成九十九，再改成一百，可以展示“大于等于”的边界。九十九万元只需财务经理；一百万元也属于需要总经理审批的分支。
三类模型在这里共同工作：M3 提供金额判断，M5 提供财务经理和总经理等角色，M6 定义审批节点和分支。角色再映射到系统中配置的用户。
流程并不是一次请求把所有人工审批瞬间跑完，而是把任务持久化，等待对应角色处理，处理完成后推进后续步骤。V9 所说的同步编排，重点是系统活动与联动的执行方式。
本页只演示通过路径，实际样例还包括驳回、退回、撤回等处理。''',
      [MODELS+'m3-rule-model.yaml', MODELS+'m5-actor-model.yaml', MODELS+'m6-flow-model.yaml', BACKEND+'engine/flow_engine.py'], chapter='案例', footer='教学模拟 · 金额阈值来自合同样例'),

    slide('M7：把“怎么看”独立建模', '跨对象读取可以自由组合，写入仍通过各自的业务行为。', '''
      <div class="two" data-check="查询模型绑定">
        <div><h3 class="subhead">查询内容由 M7 描述</h3><div class="report-sources"><span>合同</span><span>客户</span><span>部门</span></div><p class="text">来源与关联 → 过滤条件<br>→ 结果列 → 汇总与展示</p><div class="query-bind"><code>REP-CONTRACT-LIST</code><br>↕ 双向一对一<br><code>Contract_QueryList</code></div></div>
        <div><h3 class="subhead">正式报表拥有稳定定义</h3><table class="data-table"><thead><tr><th>报表</th><th>业务问题</th></tr></thead><tbody><tr><td>合同执行明细</td><td>执行到哪一步？</td></tr><tr><td>部门合同汇总</td><td>各部门金额多少？</td></tr><tr><td>已开票未收款</td><td>哪些款项尚未收到？</td></tr></tbody></table><div class="takeaway">M2 定义查询入口；<br>M7 定义查询结果的业务口径。</div></div>
      </div>''',
      '''业务系统有大量跨对象的读取需求，比如合同要连客户、部门和产品，执行报表还要汇总开票与收款。把这些读取结构塞进行为和规则，会让职责越来越混乱。
M7 专门描述数据从哪里来、如何关联、按什么条件筛选、显示哪些列和如何聚合。一个正式查询报表与一个 M2 查询行为双向一对一绑定，执行入口与查询语义因此都有稳定 ID。
这是一种建模层面的读写职责分离，不代表系统已经拆成独立读库或微服务。
AI 临时生成的动态查询可以回答探索性问题，但固定报表的正式业务口径仍然应以 M7 为依据。''',
      [MODELS+'m7-report-model.yaml', MODELS+'m2-behavior-model.yaml', BACKEND+'services/report_service.py'], chapter='案例'),

    slide('MU：让每一个按钮都有语义归属', '界面描述入口和布局，业务事实继续由其他模型负责。', '''
      <div class="two" data-check="界面语义映射">
        <div class="mock-ui" style="align-self:start"><div class="mock-title">合同登记</div><div class="mock-fields"><div class="mock-field"><span>合同名称</span><div class="mock-value">示例销售合同</div></div><div class="mock-field"><span>合同金额</span><div class="mock-value">120 万元</div></div><div class="mock-field"><span>客户</span><div class="mock-value">选择已有客户</div></div><div class="mock-field"><span>当前状态</span><div class="mock-value">草稿</div></div></div><div class="mock-actions"><span>保存草稿</span><span>提交审批</span></div></div>
        <div><div class="boundary-line" style="padding-top:0"><strong>字段与控件</strong><p>引用对象字段；关联对象用跳选，枚举和字典使用下拉选择。</p></div><div class="boundary-line"><strong>操作与行为</strong><p>保存草稿 → Contract_SaveAsDraft<br>提交审批 → Contract_Submit</p></div><div class="boundary-line"><strong>权限与可追溯性</strong><p>可见入口绑定权限；后端仍须独立校验授权与业务条件。</p></div></div>
      </div>''',
      '''MU 把总体界面、菜单、屏幕布局和操作功能点结构化。这里的关键不是自动画一个表单，而是每个操作能回到行为定义。
有审批的录入页面，规范要求保存草稿和提交两个按钮。它们对应不同动作：草稿可以继续编辑，提交会进入审批状态，不能把两个动作混在一个含糊的保存按钮里。
同样，引用对象、枚举、字典等字段有明确的控件映射。前端可以据权限控制入口，但隐藏按钮并不能代替后端授权检查。
本页是依据规范重绘的界面示意，不是现有应用截图，也不执行合同写入。''',
      [FRAMEWORK, GUIDE, MODELS+'mu-ui-model.yaml', BACKEND+'api/contract.py'], chapter='案例', footer='界面示意 · 用于解释操作与行为的映射'),

    slide('七模型，怎样落到工程实现', '模型提供语义依据，技术底座提供可复用的运行机制。', '''
      <table class="data-table compact" data-check="七模型代码映射"><thead><tr><th style="width:210px">模型</th><th style="width:590px">实现内容</th><th>仓库中的落点</th></tr></thead><tbody>
        <tr><td><b>M1 对象</b></td><td>表结构、主从关系、状态与字典</td><td><code>schema.sql / ontology/registry.py</code></td></tr>
        <tr><td><b>M2 行为</b></td><td>接口与服务、前后置条件、同步联动</td><td><code>api/ / services/ / sync_service.py</code></td></tr>
        <tr><td><b>M3 规则</b></td><td>规则表达式与领域校验函数</td><td><code>domain_rules.py / utils/rules.py</code></td></tr>
        <tr><td><b>M5 主体</b></td><td>角色权限种子与接口授权</td><td><code>seed.py / utils/security.py</code></td></tr>
        <tr><td><b>M6 流程</b></td><td>流程定义、任务、实例与状态推进</td><td><code>seed.py / engine/flow_engine.py</code></td></tr>
        <tr><td><b>M7 查询</b></td><td>固定查询、统计口径与报表</td><td><code>services/report_service.py</code></td></tr>
        <tr><td><b>MU 界面</b></td><td>菜单、路由、页面与操作点</td><td><code>frontend/src/pages/ / router/</code></td></tr>
      </tbody></table>
      <p class="mapping-note">上表基于 Python 合同样例；底座还提供系统管理、工作台和流程引擎。</p>''',
      '''这张表适合研发同事带走对照。M1 最终影响表结构和对象字段，M2 影响接口与服务，M3 影响规则表达式和领域函数，M5 影响角色权限，M6 影响流程定义和引擎，M7 影响查询，MU 影响页面与路由。
这些落点体现了模型到代码的映射，但不是说每一行都由仓库中的统一编译器自动生成。当前项目核心是一套约束 AI 开发的技能、规范、底座与完整样例。
技术底座提供身份、权限、流程、工作台等共性能力；业务扩展按项目要求发生在复制出的应用里。业务模型也不会替代数据库迁移、接口测试和真实验收。''',
      [GUIDE, BACKEND+'schema.sql', BACKEND+'seed.py', 'code-app-example/frontend/src/router/index.tsx'], chapter='工程'),

    slide('要区分：开发时生成，与运行时加载', '“模型是语义来源”，不等于“改完 YAML，整个系统立即改变”。', '''
      <div class="dual-lane" data-check="开发阶段路径"><div class="lane-label">开发阶段</div><div class="lane-track"><div class="lane-box">需求 + 模型<small>定义业务含义</small></div><div class="arrow">→</div><div class="lane-box">AI / 开发者实现<small>遵循规范和映射</small></div><div class="arrow">→</div><div class="lane-box blue-surface">服务、表、页面<small>通过联调与验收</small></div></div></div>
      <div class="dual-lane" data-check="运行阶段路径"><div class="lane-label">运行阶段</div><div class="lane-track"><div class="lane-box">manifest + YAML<small>应用启动时读取</small></div><div class="arrow">→</div><div class="lane-box">语义注册表<small>对象 / 行为 / 规则等索引</small></div><div class="arrow">→</div><div class="lane-box blue-surface">字典、流程、AI 上下文<small>具体消费路径看实现</small></div></div></div>
      <div class="takeaway" data-check="模型更新范围">修改模型之后，仍需检查服务逻辑、数据库结构、页面和测试是否同步更新。</div>''',
      '''这是最容易被误解的一页。开发阶段，AI 或开发者依据模型和指导书生成、修改业务代码；运行阶段，应用启动时从 manifest 读取 YAML，建立注册表。
registry.py 的代码很直白：按 model_type 把对象、行为、规则、角色、流程、报表和屏幕注册到字典。它提供统一的语义索引。
但它没有因此自动重建所有数据库表，也没有动态重写 React 页面。收款联动仍是服务里的显式调用，很多规则仍是函数。
所以模型变更要走影响分析和测试。讲“模型即语义来源”是准确的，讲“这里已实现全自动 YAML 编译器或热更新低代码平台”则超出了证据。''',
      [BACKEND+'app.py', BACKEND+'ontology/registry.py', BACKEND+'seed.py', BACKEND+'services/receipt_service.py'], chapter='工程'),

    slide('运行时 AI：先理解语义，再调用工具', '样例提供只读查询、统计图表和页面导航，写操作回到固定业务页面。', '''
      <div class="ai-track" data-check="运行时 AI 链路">
        <article class="ai-step"><span class="step">01</span><h3>组装业务上下文</h3><p>业务背景 + 本体注册表<br>+ 实际数据库结构<br>+ 工具能力与约束</p></article>
        <article class="ai-step"><span class="step">02</span><h3>选择只读工具</h3><p>固定列表与详情查询<br>动态只读 SQL<br>导航到业务页面</p></article>
        <article class="ai-step"><span class="step">03</span><h3>执行并返回数据</h3><p>SQL 限制 SELECT<br>检查表白名单<br>默认追加结果行数限制</p></article>
        <article class="ai-step"><span class="step">04</span><h3>流式呈现结果</h3><p>表格、图表、导航动作<br>配合文本增量输出<br>回答基于真实工具结果</p></article>
      </div>
      <div class="event-strip" data-check="真实 SSE 事件"><code>message_start → tool_call / render_payload → delta → message_end</code></div>
      <p class="source-caption">函数调用循环先执行，最终文本再流式输出。只读 SQL 的权限与资源限制仍需专项加固。</p>''',
      '''运行时 AI 的特点是知道业务语义，也知道真实表结构。prompt.py 将业务背景、注册表中的对象行为规则、实际数据库字段和工具约束组合起来。
chat.py 先进行最多五轮工具决策，拿到结果后另发一次请求流式生成最终文本。前端能收到表格、图表和导航动作。本页列出的事件来自当前实现；规范中的 tool_result 事件并未在该样例编排器中单独发出。
工具只提供读取与导航，写操作引导到固定页面。SQL 过滤包含 SELECT 限制、表白名单和缺省 LIMIT，但这不等于完整的行级授权、硬性结果上限或执行超时保障，生产使用仍要专项加固。
本体上下文能减少语义猜测，最终准确性仍依赖查询结果和权限控制。''',
      [BACKEND+'ai/prompt.py', BACKEND+'ai/chat.py', BACKEND+'ai/tools.py', BACKEND+'sql_readonly/query.py'], chapter='工程'),

    slide('真正的收益，来自持续校核', '可追溯是一项持续维护的工程纪律，而非 YAML 格式天然提供的保证。', '''
      <div class="two" style="grid-template-columns:1.12fr .88fr" data-check="门禁与边界">
        <div><div class="checklist-row"><b>入口覆盖</b><span>用户行为须有 MU 操作入口；<br>界面引用的行为必须存在。</span></div><div class="checklist-row"><b>查询一致</b><span>M7 与 M2 查询行为<br>双向一对一绑定。</span></div><div class="checklist-row"><b>流程有效</b><span>角色、行为、规则引用有效；<br>子流程调用图无环。</span></div></div>
        <div class="limits"><h3>讲清当前工程边界</h3><p>主线面向中小型单体业务系统，采用同步联动。</p><div class="divider"></div><p>规范要求 ≠ 自动校验已覆盖。<br>模型改动需要同步修改实现。</p><div class="divider"></div><p>Python / Go 底座可按项目选择；<br>本次代码分析基于 Python 合同样例。</p></div>
      </div>''',
      '''这一页建议用一个变更来收尾：假设把总经理审批阈值从一百万元改成两百万元，我们需要检查需求、M3 规则、M6 分支、流程种子或运行配置、提示词以及边界测试，而不是只改一行 YAML。
左侧是规范要求的门禁。当前注册表负责装载，并不能据此认为所有这些门禁都已经自动执行。团队可以逐步把它们变成确定性的检查脚本和持续集成任务。
同时要明确范围：V9 主线是单体同步方案，不承诺分布式一致性。仓库还有 Go 底座及其他工程能力，本次分析用 Python 合同样例验证主线，不把不同目录里的能力混为一谈。''',
      ['SKILL.md', FRAMEWORK, BACKEND+'ontology/registry.py', 'go-techbase/README.md'], chapter='工程'),

    slide('让 AI 加速实现，让模型守住业务含义', '', '''
      <div class="three" data-check="三个核心结论">
        <article><b>先形成共识</b><p>把企业专属规则确认清楚，<br>留下可建模、可验收的输入。</p></article>
        <article><b>再分离职责</b><p>用七模型表达对象、动作、<br>约束、权限、流程与入口。</p></article>
        <article><b>最后验证落地</b><p>让服务、数据和界面<br>持续对齐同一套业务语义。</p></article>
      </div>
      <div class="takeaway" data-edit="closing-message" data-check="团队实践建议">团队起步：选一条完整业务链，做一次“需求 → 模型 → 代码 → 测试”的对照评审。</div>
      <p class="text" style="margin-top:38px;color:#e3e9ff">讨论：我们现有项目里，哪一条业务规则最容易在多处产生漂移？</p>''',
      '''最后记住三句话：先形成业务共识，再用模型分离职责，最后通过代码与测试验证落地。
这个仓库的价值，是把需求探索、模型规范、技术底座和完整合同案例组织成一套可复用的开发方法。它为 AI 开发增加了共同语言和追溯链，但没有取消研发对业务边界、事务、权限和质量的责任。
团队不必一开始就重建所有系统。可以挑一个有状态变化、审批和联动的业务链，做一轮从需求到测试的对照评审，再把反复出现的规则变成自动检查。
留一个讨论问题：你们现有项目中，哪条业务规则最容易在页面、接口和流程之间失去一致性？''',
      ['README.md', 'SKILL.md', GUIDE], chapter='回顾', footer='讨论与问答', kind='closing'),

    slide('继续阅读：从这几处进入仓库', '讲解备注中保留逐页源码依据；以下为最短阅读路径。', '''
      <div class="source-grid" data-check="仓库阅读索引">
        <article class="source-group"><h3>方法全景</h3><p><a href="@@REPO@@/README.md" target="_blank" rel="noopener">README.md</a>、<a href="@@REPO@@/SKILL.md" target="_blank" rel="noopener">SKILL.md</a><br>三阶段、产物、人工确认与开发纪律。</p></article>
        <article class="source-group"><h3>模型规范</h3><p><a href="@@FRAMEWORK@@" target="_blank" rel="noopener">七模型 V9 规范</a><br>模型分工、依赖、聚合、同步联动与门禁。</p></article>
        <article class="source-group"><h3>真实业务模型</h3><p><code>code-app-example/models/</code><br>合同、开票、收款、审批、查询与界面定义。</p></article>
        <article class="source-group"><h3>联动与事务</h3><p><code>services/receipt_service.py</code><br><code>services/sync_service.py</code>、<code>db.py</code></p></article>
        <article class="source-group"><h3>运行时语义与 AI</h3><p><code>ontology/registry.py</code>、<code>ai/prompt.py</code><br><code>ai/chat.py</code>、<code>sql_readonly/query.py</code></p></article>
        <article class="source-group"><h3>完整案例验证</h3><p><a href="@@REPO@@/code-app-example/README.md" target="_blank" rel="noopener">合同样例说明</a>、<code>backend/smoke_test.py</code><br>启动方式、完整业务链和自测场景。</p></article>
      </div>
      <p class="source-caption">演示采用 frontend-slides 技能与自定义白底蓝色版式；业务分析依据当前仓库快照。</p>''',
      '''这一页是备查材料，不需要在二十分钟主讲里逐项展开。
如果同事偏方法论，从 README 和 SKILL 开始，再读七模型规范与业务开发指导书。如果偏工程实现，直接对照收款服务、同步服务、注册表和 AI 编排器。
要复现实际应用，按 code-app-example 的说明启动并运行自测。演示本身可以直接双击打开，不依赖业务系统、不需要配置大模型。
源码链接固定到制作本次演示时的 Git 提交，便于之后回看同一版本。''',
      ['README.md', 'SKILL.md', FRAMEWORK, BACKEND+'services/sync_service.py', BACKEND+'smoke_test.py'], chapter='附录', footer='源码与阅读路径'),
]

# 原有标题保留编辑键，插页后不会把本机修改错配到新主题。
for original_index, original_slide in enumerate(SLIDES, 1):
    original_slide['edit_key'] = str(original_index)

from harness_content import create_harness_slides

SLIDES[16:16] = create_harness_slides(slide, BACKEND)

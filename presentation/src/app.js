/* === 七模型说明：语义与真实样例 ID 保持对应 === */
const MODEL_DETAILS = {
  M1:{name:'对象模型',question:'业务里有哪些东西？',description:'定义业务对象、属性、生命周期与聚合边界。合同与付款阶段形成一个聚合；开票、收款拥有各自的生命周期。',example:'AGG-CONTRACT-001 · Contract'},
  M2:{name:'行为模型',question:'一次操作会改变什么？',description:'描述原子行为的前置条件、后置状态、引用规则与同步联动。跨聚合协作通过 syncTriggers 显式声明。',example:'Receipt_Record → Invoice_UpdateReceiptStatus'},
  M3:{name:'规则模型',question:'什么条件才允许成立？',description:'只判断条件，不直接修改对象。将可复用的校验与决策独立表达，再由行为或流程调用。',example:'RULE-CONTRACT-SETTLEMENT'},
  M5:{name:'主体模型',question:'谁可以做这件事？',description:'定义内部角色、权限和行为授权。流程使用角色 ID 分配任务，再由系统管理配置具体人员。',example:'PERM-RECEIPT-RECORD · ROLE-FINANCE'},
  M6:{name:'流程模型',question:'跨角色协作如何推进？',description:'定义审批流与端到端协同流。人工任务引用角色，系统任务引用行为，条件网关引用规则。',example:'FLOW-CONTRACT-APPROVAL-001'},
  M7:{name:'查询报表模型',question:'从哪些数据得到什么结果？',description:'独立定义来源、关联、条件、结果列与汇总。正式报表与 M2 查询行为双向一对一绑定。',example:'REP-CONTRACT-LIST ↔ Contract_QueryList'},
  MU:{name:'界面模型',question:'用户从哪里发起操作？',description:'定义菜单、屏幕、布局和操作功能点；通过稳定 ID 引用行为、权限等语义，不在界面里重写业务规则。',example:'frmReceiptMaintain · actSave → Receipt_Record'},
};

/* === 演示控制器：画布缩放、导航、目录和讲稿 === */
class SlidePresentation {
  constructor(){
    this.slides=[...document.querySelectorAll('.slide')];this.stage=document.getElementById('deckStage');this.currentSlide=0;this.editing=false;
    this.notesPanel=document.getElementById('notesPanel');this.outline=document.getElementById('outline');
    this.restoreEdits();this.syncTitles();this.prepareOutline();this.bindControls();
    const requested=Number(location.hash.replace('#',''));
    this.showSlide(Number.isFinite(requested)&&requested>0?requested-1:0,false);this.fit();
    addEventListener('resize',()=>this.fit());addEventListener('hashchange',()=>{const n=Number(location.hash.slice(1));if(Number.isFinite(n)&&n>=1&&n<=this.slides.length)this.showSlide(n-1,false)});
  }
  fit(){
    const notesWidth=!this.notesPanel.hidden&&innerWidth>=850?this.notesPanel.getBoundingClientRect().width:0;
    const width=innerWidth-notesWidth;const scale=Math.min(width/1920,innerHeight/1080);
    this.stage.style.transform=`translate(${(width-1920*scale)/2}px,${(innerHeight-1080*scale)/2}px) scale(${scale})`;
  }
  showSlide(index,updateHash=true){
    const value=Number(index);this.currentSlide=Math.max(0,Math.min(Number.isFinite(value)?Math.trunc(value):0,this.slides.length-1));
    this.slides.forEach((s,i)=>{const current=i===this.currentSlide;s.classList.toggle('active',current);s.classList.toggle('visible',current);s.setAttribute('aria-hidden',String(!current));s.inert=!current});
    document.getElementById('slideCount').textContent=`${String(this.currentSlide+1).padStart(2,'0')} / ${this.slides.length}`;
    document.getElementById('progressFill').style.width=`${(this.currentSlide+1)/this.slides.length*100}%`;
    document.getElementById('previous').disabled=this.currentSlide===0;document.getElementById('next').disabled=this.currentSlide===this.slides.length-1;
    document.getElementById('liveTitle').textContent=`第 ${this.currentSlide+1} 页：${this.slides[this.currentSlide].dataset.title}`;
    this.outline.querySelectorAll('[data-go]').forEach(b=>b.classList.toggle('current',Number(b.dataset.go)===this.currentSlide+1));
    this.renderNotes();if(updateHash)history.replaceState(null,'',`#${this.currentSlide+1}`);
  }
  prepareOutline(){
    const grid=document.getElementById('outlineGrid');grid.replaceChildren();this.slides.forEach((s,i)=>{const button=document.createElement('button');button.dataset.go=i+1;const n=document.createElement('span');n.textContent=`${String(i+1).padStart(2,'0')}　${s.dataset.chapter}`;button.append(n,document.createTextNode(s.dataset.title));button.addEventListener('click',()=>{this.showSlide(i);this.toggleOutline(false)});grid.append(button)});
  }
  syncTitles(){
    for(const slide of this.slides){const heading=slide.querySelector('h1[data-edit],h2[data-edit]');if(heading)slide.dataset.title=heading.textContent.trim().replace(/\s+/g,' ')}
  }
  toggleOutline(open=this.outline.hidden){this.outline.hidden=!open;if(open){this.lastFocus=document.activeElement;this.outline.querySelector('.current')?.focus()}else this.lastFocus?.focus()}
  toggleNotes(open=this.notesPanel.hidden){this.notesPanel.hidden=!open;document.getElementById('notesToggle').setAttribute('aria-pressed',String(open));this.renderNotes();this.fit()}
  renderNotes(){
    const s=this.slides[this.currentSlide];document.getElementById('notesTitle').textContent=`${this.currentSlide+1} / ${this.slides.length}　${s.dataset.title}`;
    document.getElementById('notesText').textContent=s.querySelector('.speaker-notes').textContent.trim();
    const sources=document.getElementById('notesSources');sources.replaceChildren();
    for(const reference of JSON.parse(s.dataset.sources||'[]')){const a=document.createElement('a');a.href=reference.url;a.textContent=reference.label;a.target='_blank';a.rel='noopener noreferrer';sources.append(a)}
  }
  toggleEdit(active=!this.editing){
    this.editing=active;document.body.classList.toggle('editing',active);document.getElementById('editToggle').classList.toggle('active',active);document.getElementById('editToggle').textContent=active?'完成编辑':'编辑文字';
    document.querySelectorAll('[data-edit]').forEach(el=>{el.contentEditable=String(active);el.spellcheck=false});
    if(!active){this.saveEdits();document.activeElement?.blur()}
  }
  saveEdits(){
    const edits={};document.querySelectorAll('[data-edit]').forEach(el=>edits[el.dataset.edit]=el.textContent);
    try{localStorage.setItem('ontology-deck-edits-v1',JSON.stringify(edits))}catch(e){toast('浏览器无法保存修改，请下载 HTML 文件保留。')}
    this.syncTitles();this.prepareOutline();this.renderNotes();
  }
  restoreEdits(){
    try{const edits=JSON.parse(localStorage.getItem('ontology-deck-edits-v1')||'{}');for(const el of document.querySelectorAll('[data-edit]'))if(typeof edits[el.dataset.edit]==='string')el.textContent=edits[el.dataset.edit]}catch(e){toast('本地编辑记录无法读取，已使用原始内容。')}
  }
  exportHtml(){
    this.saveEdits();const clone=document.documentElement.cloneNode(true);clone.querySelector('body').classList.remove('editing');clone.querySelectorAll('[data-edit]').forEach(el=>el.removeAttribute('contenteditable'));clone.querySelector('#outline').hidden=true;clone.querySelector('#notesPanel').hidden=true;clone.querySelector('#editToggle').classList.remove('active','show');clone.querySelector('#editToggle').textContent='编辑文字';
    const blob=new Blob(['<!doctype html>\n'+clone.outerHTML],{type:'text/html;charset=utf-8'});const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download='本体驱动开发-技术分享.html';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);toast('已下载包含当前修改的离线演示文件。');
  }
  bindControls(){
    document.getElementById('previous').onclick=()=>this.showSlide(this.currentSlide-1);document.getElementById('next').onclick=()=>this.showSlide(this.currentSlide+1);
    document.getElementById('outlineToggle').onclick=()=>this.toggleOutline();document.getElementById('closeOutline').onclick=()=>this.toggleOutline(false);this.outline.addEventListener('click',e=>{if(e.target===this.outline)this.toggleOutline(false)});
    document.getElementById('notesToggle').onclick=()=>this.toggleNotes();document.getElementById('closeNotes').onclick=()=>this.toggleNotes(false);
    document.getElementById('fullscreenToggle').onclick=async()=>{try{if(!document.fullscreenElement)await document.documentElement.requestFullscreen();else await document.exitFullscreen()}catch(e){toast('当前窗口不支持全屏，可使用浏览器全屏功能。')}};
    document.getElementById('download').onclick=()=>this.exportHtml();document.getElementById('print').onclick=()=>window.print();
    document.getElementById('editToggle').onclick=()=>this.toggleEdit();
    document.addEventListener('input',e=>{if(e.target.matches('[data-edit]'))this.saveEdits()});
    document.addEventListener('keydown',e=>{
      const typing=e.target instanceof HTMLElement&&(e.target.isContentEditable||/INPUT|TEXTAREA|SELECT/.test(e.target.tagName));
      if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='s'){e.preventDefault();this.exportHtml();return}
      if(e.key==='Escape'){if(!this.outline.hidden)this.toggleOutline(false);else if(this.editing)this.toggleEdit(false);else if(!this.notesPanel.hidden)this.toggleNotes(false);return}
      if(e.ctrlKey&&e.key==='Enter'&&this.editing){e.preventDefault();this.toggleEdit(false);return}
      if(typing)return;
      if(!this.outline.hidden){if(e.key==='Tab'){const focusable=[...this.outline.querySelectorAll('button')];const first=focusable[0],last=focusable.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}}return}
      if(this.editing)return;
      if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)&&!(e.key===' '&&e.target.closest('button'))){e.preventDefault();this.showSlide(this.currentSlide+1)}
      else if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();this.showSlide(this.currentSlide-1)}
      else if(e.key==='Home'){e.preventDefault();this.showSlide(0)}else if(e.key==='End'){e.preventDefault();this.showSlide(this.slides.length-1)}
      else if(e.key.toLowerCase()==='o')this.toggleOutline();else if(e.key.toLowerCase()==='n')this.toggleNotes();else if(e.key.toLowerCase()==='e')this.toggleEdit();else if(e.key.toLowerCase()==='f')document.getElementById('fullscreenToggle').click();
    });
    let wheelAt=0;document.querySelector('.deck-viewport').addEventListener('wheel',e=>{if(this.editing||!this.outline.hidden||e.target.closest('input,button')||Math.abs(e.deltaY)<20)return;e.preventDefault();if(Date.now()-wheelAt>650){this.showSlide(this.currentSlide+(e.deltaY>0?1:-1));wheelAt=Date.now()}},{passive:false});
    let start=null;const viewport=document.querySelector('.deck-viewport');viewport.addEventListener('touchstart',e=>{if(e.touches.length===1&&!e.target.closest('button,input,[contenteditable=true]'))start={x:e.touches[0].clientX,y:e.touches[0].clientY};else start=null},{passive:true});viewport.addEventListener('touchend',e=>{if(!start||this.editing||!this.outline.hidden)return;const dx=e.changedTouches[0].clientX-start.x,dy=e.changedTouches[0].clientY-start.y;if(Math.abs(dx)>55&&Math.abs(dx)>Math.abs(dy)*1.3)this.showSlide(this.currentSlide+(dx<0?1:-1));start=null},{passive:true});
    const hotzone=document.getElementById('editHotzone'),toggle=document.getElementById('editToggle');let hideTimer;
    for(const el of [hotzone,toggle]){el.addEventListener('mouseenter',()=>{clearTimeout(hideTimer);toggle.classList.add('show')});el.addEventListener('mouseleave',()=>{hideTimer=setTimeout(()=>{if(!this.editing)toggle.classList.remove('show')},400)})}hotzone.onclick=()=>this.toggleEdit();
  }
}

/* === 交互模型选择 === */
function selectModel(id){
  const data=MODEL_DETAILS[id];if(!data)return;
  document.querySelectorAll('[data-model]').forEach(b=>{const selected=b.dataset.model===id;b.classList.toggle('selected',selected);b.setAttribute('aria-pressed',String(selected))});
  const target=document.getElementById('modelDetail');target.replaceChildren();
  for(const [tag,className,text] of [['span','tag',`${id}　${data.name}`],['h3','',data.question],['p','',data.description],['div','example mono',data.example]]){const el=document.createElement(tag);el.className=className;el.textContent=text;target.append(el)}
}
document.querySelectorAll('[data-model]').forEach(button=>button.addEventListener('click',()=>selectModel(button.dataset.model)));selectModel('M1');

/* === 收款教学模拟：界面单位万元，内部按百分之一万元保存整数 === */
const RECEIPT_SCALE=100;
const receiptState={initial:40*RECEIPT_SCALE,invoiceAmount:100*RECEIPT_SCALE,records:[]};
function updateReceipt(message='选择收款金额，观察同一笔操作的后续联动。',error=false){
  const total=receiptState.initial+receiptState.records.reduce((a,b)=>a+b,0);const fully=total>=receiptState.invoiceAmount;const stages=document.getElementById('stagesFullyInvoiced').checked;
  document.getElementById('receivedValue').textContent=String(total/RECEIPT_SCALE);document.getElementById('invoiceState').textContent=fully?'已全部收齐':'未全部收齐';document.getElementById('contractState').textContent=fully&&stages?'已结清':'已纳入管理';document.getElementById('receiptBar').style.width=`${total/receiptState.invoiceAmount*100}%`;
  document.getElementById('receiptMessage').textContent=message;document.getElementById('receiptMessage').dataset.error=String(error);document.getElementById('reverseReceipt').disabled=receiptState.records.length===0;
}
document.getElementById('recordReceipt').onclick=()=>{
  const amount=Number(document.getElementById('receiptAmount').value);
  if(!Number.isFinite(amount)||amount<=0){updateReceipt('收款金额必须大于 0。',true);return}
  const scaled=amount*RECEIPT_SCALE,units=Math.round(scaled);
  if(Math.abs(scaled-units)>0.000001){updateReceipt('教学模拟的金额最多保留两位小数。',true);return}
  const total=receiptState.initial+receiptState.records.reduce((a,b)=>a+b,0);
  if(total+units>receiptState.invoiceAmount){updateReceipt('累计收款金额不得超过开票金额；本次未写入。',true);return}
  receiptState.records.push(units);updateReceipt('登记成功 → 重算开票收款状态 → 判断合同结清资格。');
};
document.getElementById('reverseReceipt').onclick=()=>{if(!receiptState.records.length)return;receiptState.records.pop();updateReceipt('最近一笔已冲销；按有效收款重新计算，合同状态随之恢复。')};
document.getElementById('stagesFullyInvoiced').onchange=()=>updateReceipt('结清必须同时满足：所有阶段足额开票、所有有效开票全部收齐。');
document.getElementById('resetReceipt').onclick=()=>{receiptState.records=[];document.getElementById('receiptAmount').value='60';document.getElementById('stagesFullyInvoiced').checked=true;updateReceipt()};updateReceipt();

/* === 审批规则教学模拟：100 万元为金额边界 === */
function updateApproval(){
  const value=Number(document.getElementById('contractAmount').value);const valid=Number.isFinite(value)&&value>0;const high=valid&&value>=100;
  document.getElementById('gmStep').dataset.enabled=String(high);document.getElementById('approvalDecision').textContent=!valid?'请输入大于 0 的合同金额。':high?'规则成立：财务经理 → 总经理 → 纳入管理':'规则不成立：财务经理 → 纳入管理';
}document.getElementById('contractAmount').addEventListener('input',updateApproval);updateApproval();

/* === 状态提示和启动 === */
let toastTimer;function toast(message){const target=document.getElementById('toast');if(!target)return;clearTimeout(toastTimer);target.textContent=message;target.hidden=false;toastTimer=setTimeout(()=>target.hidden=true,4000)}
window.deck=new SlidePresentation();

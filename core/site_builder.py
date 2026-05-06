from __future__ import annotations

import json
from pathlib import Path


CSS = """
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#F8F9FA;--surface:#FFFFFF;--surface-2:#F1F5F9;--border:#E2E8F0;--border-2:#CBD5E1;
  --text:#0F172A;--text-2:#334155;--text-muted:#64748B;
  --heme:#1E3A8A;--heme-bg:#EFF6FF;--heme-border:#BFDBFE;--heme-light:#3B82F6;
  --nhi:#047857;--nhi-bg:#ECFDF5;--nhi-border:#6EE7B7;
  --auth:#B45309;--auth-bg:#FFFBEB;--auth-border:#FDE68A;
  --warn:#92400E;--warn-bg:#FEF3C7;--warn-border:#FDE68A;
  --primary:#1D4ED8;--primary-hover:#1E40AF;
  --r-sm:6px;--r-md:10px;--r-lg:14px;--r-xl:18px;
}
body{font-family:'Noto Sans TC',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);line-height:1.6;font-size:15px}
.header{background:#0F172A;color:#fff;padding:.9rem 1.5rem;display:flex;align-items:center;gap:1rem;position:sticky;top:0;z-index:100}
.header-title{font-size:1.05rem;font-weight:700}
.header-sub{font-size:.75rem;color:#94A3B8;margin-left:.2rem}
.header-actions{margin-left:auto;display:flex;align-items:center;gap:.5rem}
.header-badge{background:#1E40AF;color:#BFDBFE;font-size:.72rem;font-weight:600;padding:.25rem .7rem;border-radius:20px;cursor:pointer;border:1px solid #3B82F6;white-space:nowrap}
.header-badge:hover{background:#1D4ED8}
.header-link{display:inline-flex;align-items:center;background:#111827;color:#E5E7EB;text-decoration:none;font-size:.72rem;font-weight:600;padding:.25rem .7rem;border-radius:20px;border:1px solid #374151;white-space:nowrap}
.header-link:hover{background:#1F2937}
.layout{display:flex;min-height:calc(100vh - 56px)}
.sidebar{width:220px;flex-shrink:0;background:var(--surface);border-right:1px solid var(--border);padding:1rem .75rem;position:sticky;top:56px;height:calc(100vh - 56px);overflow-y:auto}
.main{flex:1;padding:1.25rem;min-width:0}
.sidebar-section{margin-bottom:1.25rem}
.sidebar-label{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--text-muted);margin-bottom:.5rem;padding:0 .25rem}
.filter-btn{display:block;width:100%;text-align:left;padding:.4rem .65rem;border-radius:var(--r-sm);border:none;background:none;cursor:pointer;font-size:.78rem;color:var(--text-2);font-family:inherit;transition:all .15s;line-height:1.4}
.filter-btn:hover{background:var(--surface-2)}
.filter-btn.active{background:var(--heme-bg);color:var(--heme);font-weight:600}
.filter-btn .count{float:right;font-size:.68rem;background:var(--surface-2);color:var(--text-muted);border-radius:10px;padding:1px 6px}
.filter-btn.active .count{background:rgba(30,58,138,.12);color:var(--heme)}
.mol-filter{display:flex;flex-wrap:wrap;gap:.3rem}
.mol-btn{padding:.22rem .5rem;border-radius:20px;border:1px solid var(--border-2);background:var(--surface);font-size:.7rem;cursor:pointer;font-family:inherit;color:var(--text-muted);transition:all .15s}
.mol-btn:hover{border-color:var(--heme-light);color:var(--heme)}
.mol-btn.active{background:var(--heme-bg);border-color:var(--heme);color:var(--heme);font-weight:600}
.search-wrap{display:flex;gap:.5rem;margin-bottom:1rem;align-items:center}
.search-input{flex:1;padding:.5rem .85rem;border:1.5px solid var(--border);border-radius:var(--r-md);font-size:.88rem;font-family:inherit;background:var(--surface);color:var(--text)}
.search-input:focus{outline:none;border-color:var(--heme-light)}
.result-count{font-size:.78rem;color:var(--text-muted);white-space:nowrap}
.cards-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1rem}
.drug-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-lg);padding:1rem;cursor:pointer;text-align:left;font-family:inherit;transition:border-color .15s, box-shadow .15s, transform .15s}
.drug-card:hover{border-color:var(--heme-light);box-shadow:0 10px 24px rgba(15,23,42,.08);transform:translateY(-1px)}
.drug-card:focus-visible{outline:2px solid var(--heme-light);outline-offset:2px}
.drug-card-header{display:flex;align-items:flex-start;gap:.6rem;margin-bottom:.5rem}
.drug-icon{width:36px;height:36px;border-radius:var(--r-md);background:var(--heme-bg);color:var(--heme);display:flex;align-items:center;justify-content:center;font-size:.85rem;flex-shrink:0;font-weight:800;border:1px solid var(--heme-border)}
.drug-name{font-size:.9rem;font-weight:700;color:var(--text);line-height:1.3}
.drug-trade{font-size:.75rem;color:var(--text-muted);margin-top:.1rem}
.drug-tags{display:flex;flex-wrap:wrap;gap:.3rem;margin-top:.5rem}
.tag{display:inline-flex;align-items:center;font-size:.68rem;font-weight:600;padding:.18rem .5rem;border-radius:20px}
.tag-disease{background:#EFF6FF;color:#1D4ED8}
.tag-nhi{background:var(--nhi-bg);color:var(--nhi)}
.tag-auth{background:var(--auth-bg);color:var(--auth)}
.tag-mol{background:#F3E8FF;color:#7C3AED}
.tag-line{background:#F8FAFC;color:var(--text-muted);border:1px solid var(--border)}
.tag-warn{background:var(--warn-bg);color:var(--warn)}
.tag-tbd{background:#F1F5F9;color:#64748B;border:1px dashed #94A3B8}
.drug-price{font-size:.76rem;color:var(--text-muted);margin-top:.45rem;padding-top:.45rem;border-top:1px solid var(--border)}
.drug-price strong{color:var(--text-2);font-weight:600}
.drug-card-actions{display:flex;justify-content:space-between;align-items:center;gap:.5rem;margin-top:.55rem}
.mini-btn{display:inline-flex;align-items:center;justify-content:center;padding:.28rem .6rem;border-radius:999px;border:1px solid var(--border);background:var(--surface);color:var(--text-2);font-size:.72rem;font-weight:600;cursor:pointer;font-family:inherit}
.mini-btn:hover{background:var(--surface-2)}
.mini-btn.issue{border-color:#F59E0B;color:#92400E;background:#FFFBEB}
.mini-btn.issue:hover{background:#FEF3C7}
.issue-badge{font-size:.68rem;color:#B45309;background:#FFFBEB;border:1px solid #FCD34D;border-radius:999px;padding:.16rem .45rem}
.drug-card-hint{font-size:.72rem;color:var(--text-muted);margin-top:.45rem}
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:200;align-items:center;justify-content:center;padding:1rem}
.modal-overlay.open{display:flex}
.modal{background:var(--surface);border-radius:var(--r-xl);max-width:680px;width:100%;max-height:90vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,.25)}
.modal-header{padding:1.25rem 1.5rem 1rem;border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--surface);z-index:1;display:flex;align-items:flex-start;gap:.75rem}
.modal-icon{width:44px;height:44px;border-radius:var(--r-lg);background:var(--heme-bg);color:var(--heme);display:flex;align-items:center;justify-content:center;font-size:1rem;font-weight:800;flex-shrink:0;border:1px solid var(--heme-border)}
.modal-title{font-size:1.05rem;font-weight:800;color:var(--text)}
.modal-subtitle{font-size:.75rem;color:var(--text-muted);margin-top:.15rem}
.modal-close{margin-left:auto;width:32px;height:32px;border-radius:50%;border:none;background:var(--surface-2);cursor:pointer;font-size:1rem;color:var(--text-muted);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.modal-close:hover{background:var(--border)}
.modal-body{padding:1.25rem 1.5rem}
.src-tag{font-size:.65rem;font-weight:600;padding:.12rem .45rem;border-radius:10px;vertical-align:middle;margin-left:.35rem}
.src-tag-link{text-decoration:none;display:inline-flex;align-items:center}
.src-tag-link:hover{text-decoration:underline}
.src-nhi{background:var(--nhi-bg);color:var(--nhi);border:1px solid var(--nhi-border)}
.src-nccn{background:#F0F9FF;color:#0369A1;border:1px solid #BAE6FD}
.src-local{background:#ECFDF5;color:#047857;border:1px solid #A7F3D0}
.src-tbd{background:#F1F5F9;color:#64748B;border:1px dashed #CBD5E1}
.section-hd{display:flex;align-items:center;gap:.5rem;margin-bottom:.5rem}
.section-hd-label{font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:var(--text-muted)}
.section-hd .src-tag{font-size:.63rem}
.data-warn{background:var(--warn-bg);border:1px solid var(--warn-border);border-radius:var(--r-md);padding:.7rem .9rem;margin-bottom:1rem;font-size:.78rem;color:var(--warn);line-height:1.6}
.data-warn strong{display:block;margin-bottom:.2rem;font-size:.8rem}
.detail-divider{border:none;border-top:1px solid var(--border);margin:.9rem 0}
.detail-row{display:flex;gap:.5rem;margin-bottom:.35rem;align-items:flex-start}
.detail-row dt{font-size:.76rem;color:var(--text-muted);min-width:75px;flex-shrink:0;padding-top:.1rem}
.detail-row dd{font-size:.8rem;color:var(--text-2);font-weight:500}
.detail-section{margin-bottom:1.1rem}
.cond-list{list-style:none;padding:0}
.cond-list li{font-size:.8rem;color:var(--text-2);line-height:1.7;padding:.15rem 0 .15rem 1.1rem;position:relative}
.cond-list li::before{content:"\\25B8";position:absolute;left:0;color:var(--heme-light)}
.review-wrap{background:#FAFCFF;border:1px solid var(--heme-border);border-radius:var(--r-lg);padding:1rem}
.review-intro{font-size:.78rem;color:var(--text-2);margin-bottom:.8rem}
.review-card{border:1px solid var(--border);border-radius:var(--r-md);background:var(--surface);padding:.9rem;margin-bottom:.85rem}
.review-card:last-child{margin-bottom:0}
.review-card-title{font-size:.86rem;font-weight:700;color:var(--heme)}
.review-card-subtitle{font-size:.74rem;color:var(--text-muted);margin:.15rem 0 .5rem}
.review-docs{list-style:none;padding:0;margin:.45rem 0 .7rem}
.review-docs li{font-size:.76rem;color:var(--text-2);padding:.08rem 0 .08rem 1rem;position:relative}
.review-docs li::before{content:"\\2022";position:absolute;left:0;color:var(--heme-light)}
.review-note{font-size:.74rem;color:var(--text-muted);margin-bottom:.7rem}
.review-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.65rem}
.review-field{display:flex;flex-direction:column;gap:.25rem}
.review-field.full{grid-column:1/-1}
.review-field label{font-size:.74rem;font-weight:600;color:var(--text-2)}
.review-input,.review-select,.review-textarea{width:100%;padding:.45rem .55rem;border:1px solid var(--border-2);border-radius:var(--r-sm);font-size:.8rem;font-family:inherit;background:var(--surface);color:var(--text)}
.review-input:focus,.review-select:focus,.review-textarea:focus{outline:none;border-color:var(--heme)}
.review-textarea{min-height:74px;resize:vertical}
.review-actions{display:flex;justify-content:space-between;align-items:center;gap:.5rem;margin-top:.7rem;flex-wrap:wrap}
.review-actions span{font-size:.72rem;color:var(--text-muted)}
.copy-btn{padding:.35rem .75rem;background:var(--surface);color:var(--heme);border:1px solid var(--heme-border);border-radius:var(--r-sm);font-size:.76rem;font-weight:600;cursor:pointer;font-family:inherit}
.copy-btn:hover{background:var(--heme-bg)}
.admin-panel{background:#FFFDF7;border:1px solid #FCD34D;border-radius:var(--r-lg);padding:1rem}
.admin-status{font-size:.76rem;color:var(--text-2);margin-bottom:.7rem;line-height:1.6}
.admin-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.75rem}
.admin-field{display:flex;flex-direction:column;gap:.3rem}
.admin-field label{font-size:.74rem;font-weight:600;color:var(--text-muted)}
.admin-select,.admin-input,.admin-note,.admin-command{width:100%;padding:.45rem .55rem;border:1px solid var(--border);border-radius:var(--r-sm);font-size:.8rem;font-family:inherit;background:var(--surface);color:var(--text-2)}
.admin-select:focus,.admin-input:focus,.admin-note:focus,.admin-command:focus{outline:none;border-color:var(--heme)}
.admin-note,.admin-command{margin-top:.7rem}
.admin-note{min-height:72px;resize:vertical}
.admin-command{min-height:88px;white-space:pre-wrap}
.admin-actions{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:.75rem}
.secondary-btn,.ghost-btn{padding:.42rem .78rem;border-radius:var(--r-sm);font-size:.76rem;font-weight:600;cursor:pointer;font-family:inherit}
.secondary-btn{background:var(--heme);color:white;border:1px solid var(--heme)}
.secondary-btn:hover{filter:brightness(.96)}
.ghost-btn{background:var(--surface);color:var(--text-2);border:1px solid var(--border)}
.ghost-btn:hover{background:#F8FAFC}
.admin-hint{font-size:.74rem;color:var(--text-muted);margin-top:.55rem;line-height:1.6}
.issue-panel{background:#FFFDF7;border:1px solid #FCD34D;border-radius:var(--r-lg);padding:1rem}
.issue-panel .review-docs{margin:.6rem 0 0}
.issue-panel .review-docs li{padding-left:0}
.issue-panel .review-docs li::before{display:none}
.issue-meta{font-size:.74rem;color:var(--text-muted);margin-top:.2rem}
.issue-empty{font-size:.78rem;color:var(--text-muted)}
.issue-form-note{font-size:.74rem;color:var(--text-muted);margin-top:.6rem;line-height:1.6}
.review-output{margin-top:.65rem;min-height:132px;white-space:pre-wrap}
.calc-box{background:var(--heme-bg);border:1px solid var(--heme-border);border-radius:var(--r-lg);padding:1rem;margin-top:.75rem}
.calc-title{font-size:.8rem;font-weight:700;color:var(--heme);margin-bottom:.7rem}
.calc-row{display:flex;align-items:center;gap:.5rem;margin-bottom:.4rem;flex-wrap:wrap}
.calc-label{font-size:.76rem;color:var(--text-muted);min-width:90px}
.calc-input{width:75px;padding:.3rem .45rem;border:1px solid var(--heme-border);border-radius:var(--r-sm);font-size:.8rem;font-family:inherit;background:var(--surface)}
.calc-input:focus{outline:none;border-color:var(--heme)}
.calc-unit{font-size:.73rem;color:var(--text-muted)}
.calc-result{background:var(--heme);color:#fff;border-radius:var(--r-md);padding:.65rem 1rem;margin-top:.65rem;font-size:.84rem;font-weight:600;text-align:center}
.calc-result span{font-size:1.1rem;font-weight:800}
.calc-btn{padding:.35rem .75rem;background:var(--heme);color:#fff;border:none;border-radius:var(--r-sm);font-size:.78rem;font-weight:600;cursor:pointer;font-family:inherit}
.calc-btn:hover{background:var(--primary-hover)}
.cl-version{margin-bottom:1.25rem}
.cl-ver-badge{display:inline-block;background:var(--heme-bg);color:var(--heme);font-size:.73rem;font-weight:700;padding:.2rem .65rem;border-radius:20px;margin-bottom:.5rem;border:1px solid var(--heme-border)}
.cl-items{list-style:none;padding:0}
.cl-items li{font-size:.8rem;color:var(--text-2);padding:.12rem 0 .12rem 1.1rem;position:relative}
.cl-items li::before{content:"\\2736";position:absolute;left:0;color:var(--heme-light);font-size:.6rem;top:.3rem}
.empty-state{text-align:center;padding:3rem 1rem;color:var(--text-muted);grid-column:1/-1}
.empty-icon{font-size:2.5rem;margin-bottom:.75rem}
.mobile-filter-bar{display:none;flex-wrap:wrap;gap:.35rem;padding:.65rem 1rem;background:var(--surface);border-bottom:1px solid var(--border)}
@media(max-width:640px){
  .sidebar{display:none}
  .main{padding:1rem}
  .cards-grid{grid-template-columns:1fr}
  .mobile-filter-bar{display:flex;overflow-x:auto;flex-wrap:nowrap}
}
.calc-bonus-wrap{margin:.55rem 0 .3rem}
.calc-bonus-toggle{display:inline-flex;align-items:center;gap:.35rem;font-size:.8rem;color:var(--heme-light);cursor:pointer;user-select:none}
.calc-bonus-toggle input[type=checkbox]{width:14px;height:14px;cursor:pointer;accent-color:var(--nhi)}
.calc-bonus-panel{margin-top:.5rem;padding:.55rem .7rem;background:var(--nhi-bg);border:1px solid var(--nhi-border);border-radius:var(--r-sm)}
.calc-select{padding:.28rem .5rem;border:1.5px solid var(--border);border-radius:var(--r-sm);font-size:.82rem;font-family:inherit;background:var(--surface);color:var(--text);width:auto}
.calc-bonus-result{font-size:.82rem;color:var(--nhi);margin-top:.5rem;padding:.4rem .65rem;background:var(--nhi-bg);border-left:3px solid var(--nhi);border-radius:0 var(--r-sm) var(--r-sm) 0}
"""

JS_TEMPLATE = r"""
const _RAW_HD = DRUGDATA;
const _HD = JSON.parse(JSON.stringify(_RAW_HD));
const ADMIN_STORAGE_KEY = 'nhi-drug-admin-overrides-v1';
const ISSUE_STORAGE_KEY = 'nhi-drug-issue-reports-v1';
const PROJECT_REPO_URL = '__PROJECT_REPO_URL__';
const ISSUE_NEW_URL = '__ISSUE_NEW_URL__';
const ISSUE_BRIDGE_URL = '__ISSUE_BRIDGE_URL__';
let adminOverrides = {};
let localIssueReports = {};
let issueBridgeState = {available:false,message:'未檢查'};

const DISEASES=[
  {k:'all',l:'全部疾病'},
  {k:'CLL',l:'CLL 慢性淋巴性白血病'},
  {k:'lymphoma',l:'淋巴瘤 Lymphoma'},
  {k:'myeloma',l:'多發性骨髓瘤 MM'},
  {k:'CML',l:'CML 慢性骨髓性白血病'},
  {k:'AML',l:'AML 急性骨髓性白血病'},
  {k:'MDS',l:'MDS 骨髓發育不良'},
  {k:'ALL',l:'ALL 急性淋巴性白血病'},
];
const MOLS=[
  {k:'btk',l:'BTK抑制劑'},
  {k:'cd20',l:'Anti-CD20'},
  {k:'flt3',l:'FLT3'},
  {k:'ph_positive',l:'Ph+/BCR-ABL'},
  {k:'bcl2',l:'BCL-2'},
];
const DNM={CLL:'CLL',lymphoma:'淋巴瘤',myeloma:'骨髓瘤',CML:'CML',AML:'AML',MDS:'MDS',ALL:'ALL',GIST:'GIST'};
const dn=k=>DNM[k]||k;
let aDis='all',aMol=new Set(),aLine='all';
function deepClone(v){return JSON.parse(JSON.stringify(v));}
function findDrugById(list,id){return list.find(x=>String(x.id)===String(id));}
function overrideKey(drugId){return String(drugId);}
function issueKey(drugId){return String(drugId);}
function hasProjectRepo(){return !!PROJECT_REPO_URL && !PROJECT_REPO_URL.includes('__');}
function hasIssueRepo(){return !!ISSUE_NEW_URL && !ISSUE_NEW_URL.includes('__');}
function loadAdminOverrides(){try{return JSON.parse(localStorage.getItem(ADMIN_STORAGE_KEY)||'{}')||{};}catch(e){return {};}}
function saveAdminOverrides(){try{localStorage.setItem(ADMIN_STORAGE_KEY,JSON.stringify(adminOverrides));}catch(e){}}
function loadIssueReports(){try{return JSON.parse(localStorage.getItem(ISSUE_STORAGE_KEY)||'{}')||{};}catch(e){return {};}}
function saveIssueReports(){try{localStorage.setItem(ISSUE_STORAGE_KEY,JSON.stringify(localIssueReports));}catch(e){}}
function hasIssueBridge(){return !!ISSUE_BRIDGE_URL && !ISSUE_BRIDGE_URL.includes('__');}
function issueStatusMeta(status){const map={reported:{label:'待確認',pending:true,cls:'src-tbd'},confirmed:{label:'已確認',pending:true,cls:'src-local'},fixed:{label:'已修正',pending:false,cls:'src-nccn'},closed:{label:'已結案',pending:false,cls:'src-nhi'}};return map[status]||map.reported;}
function normalizeIssueTimeline(report){const timeline=(report.timeline||[]).filter(Boolean);if(timeline.length) return timeline;return [{at:report.created_at||new Date().toISOString(),action:'reported',actor:report.reporter||'',note:report.details||report.summary||'',status_to:normalizeIssueStatus(report.status)}];}
function normalizeIssueStatus(status){const mapped={open:'reported',resolved:'closed'};return mapped[status]||status||'reported';}
function normalizeIssueReport(report){const normalized={...report};normalized.status=normalizeIssueStatus(report.status);normalized.created_at=report.created_at||new Date().toISOString();normalized.updated_at=report.updated_at||normalized.created_at;normalized.timeline=normalizeIssueTimeline(normalized);normalized.sync_state=report.sync_state||((report.github_issue_number||report.github_issue_url)?'created':'local');normalized.github_issue_state=report.github_issue_state||((normalized.status==='closed')?'closed':'open');normalized.reviewer=report.reviewer||'';normalized.review_note=report.review_note||'';return normalized;}
function normalizeIssueReportStore(store){const next={};for(const [key,reports] of Object.entries(store||{})){next[key]=(reports||[]).map(normalizeIssueReport);}return next;}
function psQuote(v){return `'${String(v??'').replace(/'/g,"''")}'`;}
function escAttr(v){return escHtml(v).replace(/'/g,'&#39;');}
function uniqueValues(items){return [...new Set((items||[]).filter(Boolean))];}
function fmtDateTime(v){if(!v) return '';const m=v.toString().match(/^(\d{4})-(\d{2})-(\d{2})T?(\d{2})?:?(\d{2})?/);if(!m) return v;const hh=m[4]||'00';const mm=m[5]||'00';return `${m[1]}/${m[2]}/${m[3]} ${hh}:${mm}`;}
function findFormulation(drug,formulationId){return (drug.formulations||[]).find(f=>f.formulation_id===formulationId);}
function buildFormulationCommand(drug,formulation,verifiedBy,note){if(!drug||!formulation) return '';const code=uniqueValues(formulation.nhi_drug_codes||[formulation.nhi_drug_code])[0]||'';const parts=['python scripts\\confirm_drug_formulation.py','--drug',psQuote(drug.generic_name)];if(code) parts.push('--drug-code',psQuote(code));if(formulation.label) parts.push('--label',psQuote(formulation.label));if(verifiedBy) parts.push('--verified-by',psQuote(verifiedBy));if(note) parts.push('--note',psQuote(note));return parts.join(' ');}
function stripNtuhSelection(ntuhOpenData){const src=ntuhOpenData||{};return {source_name:src.source_name||'',source_url:src.source_url||'',query_date:src.query_date||'',matched_rows_count:src.matched_rows_count||0,search_terms:src.search_terms||[],last_synced_at:src.last_synced_at||''};}
function applyPrimaryFormulationSnapshot(drug,formulation){if(!drug||!formulation) return drug;(drug.formulations||[]).forEach(f=>{f.is_primary=f.formulation_id===formulation.formulation_id;});const codes=uniqueValues(formulation.nhi_drug_codes||[formulation.nhi_drug_code]);drug.price_unit=formulation.label||drug.price_unit;if(typeof formulation.nhi_price==='number') drug.nhi_price=formulation.nhi_price;drug.nhi_drug_codes=codes.length?codes:(drug.nhi_drug_codes||[]);drug.nhi_open_data=drug.nhi_open_data||{};if(codes[0]) drug.nhi_open_data.display_drug_code=codes[0];if(formulation.nhi_effective_date) drug.nhi_open_data.display_start_date=formulation.nhi_effective_date;if(typeof formulation.ntuh_self_pay_price==='number'){drug.ntuh_self_pay_price=formulation.ntuh_self_pay_price;drug.ntuh_price_unit=formulation.label||drug.ntuh_price_unit;drug.ntuh_open_data=drug.ntuh_open_data||{};if(formulation.ntuh_query_date) drug.ntuh_open_data.query_date=formulation.ntuh_query_date;}else{drug.ntuh_self_pay_price=null;drug.ntuh_price_unit=null;drug.ntuh_open_data=stripNtuhSelection(drug.ntuh_open_data);}drug.catalog_meta={...(drug.catalog_meta||{}),primary_formulation_source:(drug.local_admin_override?'local-admin':((drug.manual_review||{}).primary_formulation_confirmed?'manual':'auto')),primary_formulation_label:drug.price_unit,primary_nhi_drug_code:codes[0]||null};return drug;}
function buildDrugWithOverride(baseDrug,override){const drug=deepClone(baseDrug);const formulation=findFormulation(drug,override?.formulation_id);if(!formulation) return drug;drug.local_admin_override={formulation_id:formulation.formulation_id,verified_by:override.verified_by||'',note:override.note||'',applied_at:override.applied_at||new Date().toISOString()};drug.manual_review={...(drug.manual_review||{}),primary_formulation_confirmed:true,multi_formulation_pending:false,canonical_decision:'confirmed',confirmed_drug_code:uniqueValues(formulation.nhi_drug_codes||[formulation.nhi_drug_code])[0]||null,confirmed_formulation_label:formulation.label||null,last_verified_at:drug.local_admin_override.applied_at,verified_by:override.verified_by||null,checked_fields:uniqueValues([...(drug.manual_review?.checked_fields||[]),'formulation','nhi_price']),local_override_pending_persist:true};if(override.note){const existing=(drug.manual_review.notes||'').trim();drug.manual_review.notes=existing?`${existing}\n${override.note}`:override.note;}return applyPrimaryFormulationSnapshot(drug,formulation);}
function restoreDrugFromRaw(drugId){const raw=findDrugById(_RAW_HD,drugId);const idx=_HD.findIndex(x=>String(x.id)===String(drugId));if(!raw||idx<0) return null;const restored=deepClone(raw);_HD[idx]=restored;return restored;}
function applyStoredOverrides(){for(const [drugId,override] of Object.entries(adminOverrides)){const raw=findDrugById(_RAW_HD,drugId);const idx=_HD.findIndex(x=>String(x.id)===String(drugId));if(!raw||idx<0) continue;_HD[idx]=buildDrugWithOverride(raw,override);}}
function getLocalIssueReports(drugId){return (localIssueReports[issueKey(drugId)]||[]).map(normalizeIssueReport).slice().sort((a,b)=>(b.created_at||'').localeCompare(a.created_at||''));}
function countPendingReports(drug){const localOpen=getLocalIssueReports(drug.id).filter(item=>issueStatusMeta(item.status).pending).length;const basePending=drug.issue_tracking?.pending_count||0;return basePending+localOpen;}
function hasPendingReports(drug){return !!(drug.issue_tracking?.has_pending_error||countPendingReports(drug)>0);}
function latestIssueReportedAt(drug){const localLatest=getLocalIssueReports(drug.id)[0]?.updated_at||getLocalIssueReports(drug.id)[0]?.created_at||'';const baseLatest=drug.issue_tracking?.latest_reported_at||'';return [localLatest,baseLatest].filter(Boolean).sort().reverse()[0]||'';}
function buildIssueTitle(drug,report){return `[Drug data] ${drug.generic_name} - ${report.summary||report.field}`;}
function buildIssueLabels(report){return uniqueValues(['drug-data',`status:${normalizeIssueStatus(report.status)}`,report.severity?`severity:${report.severity}`:'',report.field?`field:${report.field}`:''].filter(Boolean));}
function buildIssuePayload(drug,form){const createdAt=new Date().toISOString();const formulation=primaryFormulation(drug);const payload={id:`issue-${drug.id}-${Date.now()}`,status:'reported',created_at:createdAt,updated_at:createdAt,reporter:form.reporter||'',reviewer:'',review_note:'',field:form.field||'other',severity:form.severity||'normal',summary:form.summary||'',details:form.details||'',source_url:form.source_url||'',selected_formulation_label:formulation?.label||'',selected_nhi_drug_code:(drug.nhi_open_data?.display_drug_code||drug.nhi_drug_codes?.[0]||''),nhi_effective_date:primaryEffectiveDate(drug)||'',ntuh_query_date:drug.ntuh_open_data?.query_date||'',github_issue_url:'',github_issue_number:null,github_issue_state:'open',sync_state:'local',last_sync_at:null,timeline:[{at:createdAt,action:'reported',actor:form.reporter||'',note:form.details||form.summary||'',status_to:'reported'}]};payload.github_issue_url=buildGitHubIssueUrl(drug,payload);return payload;}
function buildIssueBody(drug,report){return [`藥物：${drug.generic_name}`,`Trade name：${drug.trade_names||''}`,`通報欄位：${report.field}`,`嚴重度：${report.severity}`,`目前狀態：${issueStatusMeta(report.status).label}`,`目前主劑型：${report.selected_formulation_label||''}`,`目前健保代碼：${report.selected_nhi_drug_code||''}`,`健保生效日：${fmtRocDate(report.nhi_effective_date)||report.nhi_effective_date||''}`,`台大查詢日：${fmtIsoDate(report.ntuh_query_date)||report.ntuh_query_date||''}`,report.source_url?`參考來源：${report.source_url}`:'',`摘要：${report.summary}`,`詳細說明：\n${report.details||''}`,report.reporter?`通報者：${report.reporter}`:'',report.reviewer?`審核者：${report.reviewer}`:'',report.review_note?`審核備註：${report.review_note}`:''].filter(Boolean).join('\n');}
function buildIssueComment(drug,report,actionLabel){return [`${actionLabel}｜${drug.generic_name}`,`狀態：${issueStatusMeta(report.status).label}`,report.reviewer?`審核者：${report.reviewer}`:'',report.review_note?`審核備註：${report.review_note}`:'',`同步時間：${fmtDateTime(new Date().toISOString())}`].filter(Boolean).join('\n');}
function buildGitHubIssueUrl(drug,report){if(!hasIssueRepo()) return '';const params=new URLSearchParams({title:buildIssueTitle(drug,report),body:buildIssueBody(drug,report)});return `${ISSUE_NEW_URL}?${params.toString()}`;}
async function issueBridgeRequest(path,method,payload){if(!hasIssueBridge()) throw new Error('未設定 issue bridge');const res=await fetch(`${ISSUE_BRIDGE_URL}${path}`,{method,headers:{'Content-Type':'application/json'},body:payload?JSON.stringify(payload):undefined});const data=await res.json().catch(()=>({}));if(!res.ok) throw new Error(data.error||data.message||`HTTP ${res.status}`);return data;}
async function detectIssueBridge(){if(!hasIssueBridge()){issueBridgeState={available:false,message:'未設定 bridge'};return issueBridgeState;}try{const data=await issueBridgeRequest('/health','GET');issueBridgeState={available:true,message:`Bridge 已連線：${data.repo||'repo 未知'}`};}catch(e){issueBridgeState={available:false,message:`Bridge 不可用：${e.message}`};}return issueBridgeState;}
function upsertLocalIssueReport(drugId,report){const key=issueKey(drugId);const reports=getLocalIssueReports(drugId).filter(item=>item.id!==report.id);localIssueReports[key]=[normalizeIssueReport(report),...reports];saveIssueReports();}
function appendIssueTimeline(report,entry){report.timeline=[...(report.timeline||[]),entry];report.updated_at=entry.at||new Date().toISOString();return report;}
function cntDis(k){return k==='all'?_HD.length:_HD.filter(d=>(d.clinical_tags?.disease||[]).includes(k)).length;}
function renderSidebar(){
  document.getElementById('dFilt').innerHTML=DISEASES.map(d=>`<button class="filter-btn${aDis===d.k?' active':''}" onclick="setDis('${d.k}')">${d.l}<span class="count">${cntDis(d.k)}</span></button>`).join('');
  document.getElementById('mFilt').innerHTML=MOLS.map(m=>`<button class="mol-btn${aMol.has(m.k)?' active':''}" onclick="toggleMol('${m.k}')">${m.l}</button>`).join('');
  document.getElementById('lFilt').innerHTML=[['all','全部'],['1','第一線'],['2','第二線'],['3','第三線+']].map(([l,lb])=>`<button class="filter-btn${aLine===l?' active':''}" onclick="setLine('${l}')">${lb}</button>`).join('');
  document.getElementById('mobFilt').innerHTML=DISEASES.map(d=>`<button class="mol-btn${aDis===d.k?' active':''}" onclick="setDis('${d.k}')" style="white-space:nowrap">${d.k==='all'?'全部':d.k}</button>`).join('');
}
function setDis(k){aDis=k;renderSidebar();renderCards();}
function toggleMol(k){aMol.has(k)?aMol.delete(k):aMol.add(k);renderSidebar();renderCards();}
function setLine(l){aLine=l;renderSidebar();renderCards();}
function getFilt(){
  const q=(document.getElementById('sIn')?.value||'').trim().toLowerCase();
  return _HD.filter(d=>{
    const dis=d.clinical_tags?.disease||[];
    if(aDis!=='all'&&!dis.includes(aDis)) return false;
    if(aMol.size>0&&![...aMol].every(m=>d.clinical_tags?.[m])) return false;
    if(aLine==='1'&&(d.therapy_line||1)>1) return false;
    if(aLine==='2'&&d.therapy_line!==2) return false;
    if(aLine==='3'&&(d.therapy_line||1)<3) return false;
    if(q&&!(d.generic_name+' '+(d.trade_names||'')+' '+d.indication+' '+(dis.join(' '))).toLowerCase().includes(q)) return false;
    return true;
  });
}
function ini(n){const w=n.split(/[\s\-]+/);return w.length>=2?(w[0][0]+(w[1][0]||'')).toUpperCase():n.substring(0,2).toUpperCase();}
function molT(d){const r=[];if(d.clinical_tags?.btk) r.push('<span class="tag tag-mol">BTK</span>');if(d.clinical_tags?.cd20) r.push('<span class="tag tag-mol">CD20</span>');if(d.clinical_tags?.flt3) r.push('<span class="tag tag-mol">FLT3</span>');if(d.clinical_tags?.ph_positive) r.push('<span class="tag tag-mol">Ph+</span>');if(d.clinical_tags?.bcl2) r.push('<span class="tag tag-mol">BCL-2</span>');return r.join('');}
function lineSrcTag(src){if(src==='健保規定') return '<span class="src-tag src-nhi">健保規定</span>';if(src==='NCCN') return '<span class="src-tag src-nccn">NCCN</span>';return '<span class="src-tag src-tbd">待確認</span>';}
function recSrcTag(src){if(src==='NHI') return '<span class="src-tag src-nhi">健保</span>';if(src==='NCCN' || src==='Guideline') return '<span class="src-tag src-nccn">指引</span>';if(src==='NTUH' || src==='Local') return '<span class="src-tag src-local">院內</span>';return '<span class="src-tag src-tbd">待確認</span>';}
function fmtRocDate(v){const s=(v||'').toString().replace(/\D/g,'');if(s.length!==7) return '';return `${s.slice(0,3)}/${s.slice(3,5)}/${s.slice(5,7)}`;}
function fmtIsoDate(v){if(!v) return '';const m=v.toString().match(/^(\d{4})-(\d{2})-(\d{2})/);return m?`${m[1]}/${m[2]}/${m[3]}`:'';}
function primaryFormulation(d){return (d.formulations||[]).find(f=>f.is_primary) || d.formulations?.[0] || null;}
function primaryNhiPrice(d){const value=primaryFormulation(d)?.nhi_price;return typeof value==='number' ? value : d.nhi_price;}
function primaryEffectiveDate(d){return primaryFormulation(d)?.nhi_effective_date || d.nhi_open_data?.display_start_date || d.nhi_open_data?.selected_start_date || '';}
function displayPriceUnit(d){return primaryFormulation(d)?.label || d.price_unit || 'unit';}
function formulationWarnText(d){if(!d.manual_review?.multi_formulation_pending) return '';const count=d.manual_review?.candidate_formulation_count||d.formulations?.length||0;return `同成分目前有 ${count} 個候選劑型，主劑型與價格需人工確認。`;}
function escHtml(v){return (v??'').toString().replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function linkTag(url,label,cls){if(!url) return `<span class="src-tag ${cls}">${label}</span>`;return `<a class="src-tag src-tag-link ${cls}" href="${escHtml(url)}" target="_blank" rel="noopener noreferrer">${label}</a>`;}
function reviewFieldId(drugId,profileId,key){return `rv-${drugId}-${profileId}-${key}`;}
function reviewSummaryId(drugId,profileId){return `rvout-${drugId}-${profileId}`;}
function renderReviewField(drugId,profile){return profile.fields.map(f=>{const fid=reviewFieldId(drugId,profile.id,f.key);const cls=(f.type==='textarea')?'review-field full':'review-field';if(f.type==='select'){return `<div class="${cls}"><label for="${fid}">${f.label}</label><select class="review-select" id="${fid}" onchange="buildReviewSummary(${drugId},'${profile.id}')"><option value="">${f.placeholder||'請選擇'}</option>${(f.options||[]).map(opt=>`<option value="${escHtml(opt.value)}">${escHtml(opt.label)}</option>`).join('')}</select></div>`;}if(f.type==='textarea'){return `<div class="${cls}"><label for="${fid}">${f.label}</label><textarea class="review-textarea" id="${fid}" placeholder="${escHtml(f.placeholder||'')}" oninput="buildReviewSummary(${drugId},'${profile.id}')"></textarea></div>`;}return `<div class="${cls}"><label for="${fid}">${f.label}</label><input class="review-input" id="${fid}" type="${f.type||'text'}" step="${escHtml(f.step||'1')}" placeholder="${escHtml(f.placeholder||'')}" oninput="buildReviewSummary(${drugId},'${profile.id}')"></div>`;}).join('');}
function renderReviewSupport(d){const rs=d.review_support;if(!rs?.profiles?.length) return '';return `<div class="detail-section"><div class="section-hd"><span class="section-hd-label">審查資料整理</span></div><div class="review-wrap"><div class="review-intro">${escHtml(rs.intro||'')}</div>${rs.profiles.map(profile=>`<div class="review-card"><div class="review-card-title">${escHtml(profile.label)}</div>${profile.subtitle?`<div class="review-card-subtitle">${escHtml(profile.subtitle)}</div>`:''}${profile.docs?.length?`<ul class="review-docs">${profile.docs.map(doc=>`<li>${escHtml(doc)}</li>`).join('')}</ul>`:''}${profile.note?`<div class="review-note">${escHtml(profile.note)}</div>`:''}<div class="review-grid">${renderReviewField(d.id,profile)}</div><div class="review-actions"><span>填寫後會自動整理成可複製的送審摘要。</span><button class="copy-btn" type="button" onclick="copyReviewSummary(${d.id},'${profile.id}')">複製摘要</button></div><textarea class="review-textarea review-output" id="${reviewSummaryId(d.id,profile.id)}" readonly></textarea></div>`).join('')}</div></div>`;}
function buildReviewSummary(drugId,profileId){const drug=_HD.find(x=>x.id===drugId);const profile=drug?.review_support?.profiles?.find(p=>p.id===profileId);const out=document.getElementById(reviewSummaryId(drugId,profileId));if(!profile||!out) return;const lines=[`${drug.generic_name}｜${profile.label}`];if(profile.subtitle) lines.push(`適用情境：${profile.subtitle}`);lines.push('送審重點：');let hasFilled=false;for(const field of (profile.fields||[])){const el=document.getElementById(reviewFieldId(drugId,profileId,field.key));if(!el) continue;const raw=(el.value||'').trim();if(!raw) continue;hasFilled=true;let display=raw;if(field.type==='select'){display=el.options?.[el.selectedIndex]?.text||raw;}lines.push(`- ${field.label}：${display}`);}if(!hasFilled){lines.push('- 尚未填入病人資料');}if(profile.docs?.length){lines.push('建議檢附文件：');for(const doc of profile.docs) lines.push(`- ${doc}`);}lines.push('提醒：本段為送審草稿整理，仍需對照最新健保給付規定與正式病歷。');out.value=lines.join('\n');}
function initReviewSupport(drug){for(const profile of (drug.review_support?.profiles||[])){buildReviewSummary(drug.id,profile.id);}}
function copyReviewSummary(drugId,profileId){const out=document.getElementById(reviewSummaryId(drugId,profileId));if(!out) return;out.select();out.setSelectionRange(0,out.value.length);if(navigator.clipboard?.writeText){navigator.clipboard.writeText(out.value).catch(()=>document.execCommand('copy'));}else{document.execCommand('copy');}}
function renderRecommendationSources(d){const sources=d.recommendation_sources||[];if(!sources.length) return '';return `<div class="detail-section"><div class="section-hd"><span class="section-hd-label">來源與建議</span><span class="src-tag src-nhi">版本化</span></div><div class="review-wrap">${sources.map(source=>{const categoryMap={coverage_line:'治療線/給付',self_pay_pricing:'院內價格',general:'一般參考',recommendation:'指引建議'};const versions=(source.versions||[]).slice().sort((a,b)=>(b.effective_or_query_date||'').localeCompare(a.effective_or_query_date||''));return `<div class="review-card"><div class="review-card-title">${escHtml(source.source_name||'未命名來源')} ${recSrcTag(source.source_type)}</div><div class="review-card-subtitle">${escHtml(categoryMap[source.category]||source.category||'一般參考')}｜共 ${versions.length} 個版本</div><ul class="review-docs">${versions.map(v=>{const codes=(v.reference_codes||[]).filter(Boolean);const date=fmtRocDate(v.effective_or_query_date)||fmtIsoDate(v.effective_or_query_date)||'未標日期';const note=[codes.length?`章節/代碼：${codes.join('、')}`:'', v.evidence_note||''].filter(Boolean).join(' ');return `<li><strong>${escHtml(date)}</strong>｜${escHtml(v.recommendation||'未提供建議')}${note?`<div class="review-note">${escHtml(note)}</div>`:''}</li>`;}).join('')}</ul></div>`;}).join('')}</div></div>`;}
function renderRecordVersions(d){const versions=(d.record_versions||[]).slice().sort((a,b)=>(b.event_at||'').localeCompare(a.event_at||'')).slice(0,8);if(!versions.length) return '';return `<div class="detail-section"><div class="section-hd"><span class="section-hd-label">版本紀錄</span><span class="src-tag src-local">留存</span></div><div class="review-wrap"><ul class="review-docs">${versions.map(v=>`<li><strong>${escHtml(fmtDateTime(v.event_at)||v.event_at||'未標時間')}</strong>｜${escHtml(v.summary||v.event_type||'未命名事件')}<div class="review-note">來源：${escHtml(v.source||'local')}｜版本：${escHtml(v.version||'')}</div></li>`).join('')}</ul></div></div>`;}
function issueReportStatusId(reportId){return `issue-status-${reportId}`;}
function issueReportReviewerId(reportId){return `issue-reviewer-${reportId}`;}
function issueReportNoteId(reportId){return `issue-note-${reportId}`;}
function issueTimelineHtml(report){const timeline=(report.timeline||[]).slice().sort((a,b)=>(b.at||'').localeCompare(a.at||''));if(!timeline.length) return '';return `<ul class="review-docs">${timeline.map(item=>`<li><strong>${escHtml(fmtDateTime(item.at)||item.at||'')}</strong>｜${escHtml(item.action||'update')}${item.status_to?`<div class="issue-meta">狀態：${escHtml(issueStatusMeta(item.status_to).label)}</div>`:''}${item.actor?`<div class="issue-meta">執行者：${escHtml(item.actor)}</div>`:''}${item.note?`<div class="review-note">${escHtml(item.note)}</div>`:''}</li>`).join('')}</ul>`;}
async function createGitHubIssueForReport(drugId,reportId){const drug=findDrugById(_HD,drugId);let report=getLocalIssueReports(drugId).find(item=>item.id===reportId);if(!drug||!report) return;if(!issueBridgeState.available){alert(issueBridgeState.message||'Issue bridge 不可用');return;}try{const data=await issueBridgeRequest('/issues','POST',{title:buildIssueTitle(drug,report),body:buildIssueBody(drug,report),labels:buildIssueLabels(report)});report={...report,github_issue_url:data.html_url||data.url||report.github_issue_url,github_issue_number:data.number||report.github_issue_number,github_issue_state:data.state||'open',sync_state:'created',last_sync_at:new Date().toISOString()};appendIssueTimeline(report,{at:report.last_sync_at,action:'issue_created',actor:report.reviewer||report.reporter||'system',note:`建立 GitHub issue #${report.github_issue_number||''}`});upsertLocalIssueReport(drugId,report);renderSidebar();renderCards();showDet(drugId);}catch(e){report={...report,sync_state:'error',last_sync_at:new Date().toISOString()};appendIssueTimeline(report,{at:report.last_sync_at,action:'issue_error',actor:report.reviewer||report.reporter||'system',note:e.message});upsertLocalIssueReport(drugId,report);renderSidebar();renderCards();showDet(drugId);alert(`GitHub 開單失敗：${e.message}`);}}
async function syncGitHubIssueForReport(drugId,reportId,actionLabel='同步審核狀態'){const drug=findDrugById(_HD,drugId);let report=getLocalIssueReports(drugId).find(item=>item.id===reportId);if(!drug||!report) return;if(!issueBridgeState.available){alert(issueBridgeState.message||'Issue bridge 不可用');return;}if(!report.github_issue_number){await createGitHubIssueForReport(drugId,reportId);report=getLocalIssueReports(drugId).find(item=>item.id===reportId);if(!report?.github_issue_number) return;}try{const desiredState=report.status==='closed'?'closed':'open';const patch=await issueBridgeRequest(`/issues/${report.github_issue_number}`,'PATCH',{state:desiredState,labels:buildIssueLabels(report),title:buildIssueTitle(drug,report),body:buildIssueBody(drug,report)});await issueBridgeRequest(`/issues/${report.github_issue_number}/comments`,'POST',{body:buildIssueComment(drug,report,actionLabel)});report={...report,github_issue_url:patch.html_url||report.github_issue_url,github_issue_state:patch.state||desiredState,sync_state:'updated',last_sync_at:new Date().toISOString()};appendIssueTimeline(report,{at:report.last_sync_at,action:'issue_synced',actor:report.reviewer||report.reporter||'system',note:`GitHub issue #${report.github_issue_number} 已同步`,status_to:report.status});upsertLocalIssueReport(drugId,report);renderSidebar();renderCards();showDet(drugId);}catch(e){report={...report,sync_state:'error',last_sync_at:new Date().toISOString()};appendIssueTimeline(report,{at:report.last_sync_at,action:'issue_error',actor:report.reviewer||report.reporter||'system',note:e.message,status_to:report.status});upsertLocalIssueReport(drugId,report);renderSidebar();renderCards();showDet(drugId);alert(`GitHub 同步失敗：${e.message}`);}}
function applyIssueReview(drugId,reportId){const report=getLocalIssueReports(drugId).find(item=>item.id===reportId);if(!report) return;const nextStatus=document.getElementById(issueReportStatusId(reportId))?.value||report.status;const reviewer=(document.getElementById(issueReportReviewerId(reportId))?.value||'').trim();const reviewNote=(document.getElementById(issueReportNoteId(reportId))?.value||'').trim();const updated={...report,status:normalizeIssueStatus(nextStatus),reviewer,review_note:reviewNote,updated_at:new Date().toISOString()};appendIssueTimeline(updated,{at:updated.updated_at,action:'status_changed',actor:reviewer||'reviewer',note:reviewNote,status_to:updated.status});upsertLocalIssueReport(drugId,updated);renderSidebar();renderCards();showDet(drugId);}
function renderIssueTracking(d){const localReports=getLocalIssueReports(d.id);const pendingCount=countPendingReports(d);const latest=latestIssueReportedAt(d);const latestText=latest?fmtDateTime(latest):'尚無';const issueUrl=(d.issue_tracking?.open_issue_urls||[])[0]||localReports[0]?.github_issue_url||'';const tag=pendingCount?'<span class="src-tag src-tbd">待確認</span>':'<span class="src-tag src-nhi">無待處理</span>';const bridgeTag=`<span class="src-tag ${issueBridgeState.available?'src-local':'src-tbd'}">${escHtml(issueBridgeState.message||'bridge 未檢查')}</span>`;const reportItems=localReports.length?localReports.map(item=>{const statusMeta=issueStatusMeta(item.status);const statusOptions=['reported','confirmed','fixed','closed'].map(status=>`<option value="${status}"${item.status===status?' selected':''}>${issueStatusMeta(status).label}</option>`).join('');const syncText=item.github_issue_number?`GitHub issue #${item.github_issue_number}`:'尚未建立 GitHub issue';return `<div class="review-card"><div class="review-card-title">${escHtml(item.summary||'未填摘要')} <span class="src-tag ${statusMeta.cls}">${statusMeta.label}</span></div><div class="review-card-subtitle">欄位：${escHtml(item.field||'other')}｜嚴重度：${escHtml(item.severity||'normal')}｜${escHtml(syncText)}</div>${item.details?`<div class="review-note">${escHtml(item.details)}</div>`:''}<div class="issue-meta">通報者：${escHtml(item.reporter||'未填')}｜建立：${escHtml(fmtDateTime(item.created_at)||item.created_at||'')}</div><div class="issue-meta">同步狀態：${escHtml(item.sync_state||'local')}${item.last_sync_at?`｜上次同步：${escHtml(fmtDateTime(item.last_sync_at)||item.last_sync_at)}`:''}</div><div class="admin-grid" style="margin-top:.7rem"><div class="admin-field"><label for="${issueReportStatusId(item.id)}">審核狀態</label><select class="admin-select" id="${issueReportStatusId(item.id)}">${statusOptions}</select></div><div class="admin-field"><label for="${issueReportReviewerId(item.id)}">審核者</label><input class="admin-input" id="${issueReportReviewerId(item.id)}" type="text" value="${escAttr(item.reviewer||'')}" placeholder="例如 TH"></div></div><div class="admin-field"><label for="${issueReportNoteId(item.id)}">審核備註</label><textarea class="admin-note" id="${issueReportNoteId(item.id)}" placeholder="例如：已核對官方 PDF，確認應改用 100mg/vial">${escHtml(item.review_note||'')}</textarea></div><div class="admin-actions"><button class="secondary-btn" type="button" onclick="applyIssueReview(${d.id},'${item.id}')">更新審核狀態</button><button class="copy-btn" type="button" onclick="syncGitHubIssueForReport(${d.id},'${item.id}')">${item.github_issue_number?'同步 GitHub':'建立 GitHub issue'}</button>${item.github_issue_url?`<a class="ghost-btn" href="${escHtml(item.github_issue_url)}" target="_blank" rel="noopener noreferrer">開啟 Issue</a>`:''}</div>${issueTimelineHtml(item)}</div>`;}).join(''):'<div class="issue-empty">目前沒有本機通報紀錄。</div>';const actions=`<div class="admin-actions"><button class="secondary-btn" type="button" onclick="openIssueReporter(${d.id})">通報錯誤</button>${issueUrl?`<a class="copy-btn" href="${escHtml(issueUrl)}" target="_blank" rel="noopener noreferrer">查看 Issue</a>`:''}</div>`;return `<div class="detail-section"><div class="section-hd"><span class="section-hd-label">錯誤通報</span>${tag}${bridgeTag}</div><div class="issue-panel"><div class="admin-status">待處理通報：${pendingCount} 筆｜最新通報：${latestText}</div>${actions}${reportItems}<div class="issue-form-note">完整流程：待確認 → 已確認 → 已修正 → 已結案。若 localhost GitHub bridge 已啟動，通報與審核結果可直接同步到 GitHub Issues。</div></div></div>`;}
function issueFieldOptions(){return [['nhi_price','健保價'],['ntuh_price','台大自費價'],['formulation','劑型 / 規格'],['rule_text','健保條文'],['indication','適應症'],['therapy_line','治療線'],['prior_auth','事前審查條件'],['other','其他']].map(([v,l])=>`<option value="${v}">${l}</option>`).join('');}
function issueSeverityOptions(){return [['normal','一般'],['high','高'],['blocking','阻擋使用']].map(([v,l])=>`<option value="${v}">${l}</option>`).join('');}
function issueSummaryId(){return 'issue-summary';}
function issueDetailId(){return 'issue-detail';}
function issueFieldId(){return 'issue-field';}
function issueSeverityId(){return 'issue-severity';}
function issueReporterId(){return 'issue-reporter';}
function issueSourceId(){return 'issue-source';}
function issueDrugId(){return 'issue-drug-id';}
function issueGithubLinkId(){return 'issue-github-link';}
function openIssueReporter(drugId){const d=findDrugById(_HD,drugId);if(!d) return;const bridgeMessage=issueBridgeState.available?'送出後會直接透過 localhost GitHub bridge 建立 issue。':'目前 bridge 不可用；通報會先留存在本機，之後可再同步。';const el=document.getElementById('issueC');el.innerHTML=`<div class="modal-header"><div class="modal-icon">&#9888;</div><div style="flex:1"><div class="modal-title">錯誤通報</div><div class="modal-subtitle">${escHtml(d.generic_name)} &middot; ${escHtml(d.trade_names||'(通用名)')}</div></div><button class="modal-close" onclick="closeIssueModal()">&#x2715;</button></div><div class="modal-body"><input id="${issueDrugId()}" type="hidden" value="${escAttr(d.id)}"><div class="admin-grid"><div class="admin-field"><label for="${issueFieldId()}">欄位</label><select class="admin-select" id="${issueFieldId()}">${issueFieldOptions()}</select></div><div class="admin-field"><label for="${issueSeverityId()}">嚴重度</label><select class="admin-select" id="${issueSeverityId()}">${issueSeverityOptions()}</select></div><div class="admin-field"><label for="${issueReporterId()}">通報者</label><input class="admin-input" id="${issueReporterId()}" type="text" placeholder="例如 TH"></div><div class="admin-field"><label for="${issueSourceId()}">參考連結</label><input class="admin-input" id="${issueSourceId()}" type="url" placeholder="原始文件或頁面連結"></div></div><div class="admin-field"><label for="${issueSummaryId()}">摘要</label><input class="admin-input" id="${issueSummaryId()}" type="text" placeholder="例如：Azacitidine 目前選到口服 Onureg，不是 Vidaza 注射劑"></div><div class="admin-field"><label for="${issueDetailId()}">詳細說明</label><textarea class="admin-note" id="${issueDetailId()}" placeholder="請盡量寫清楚錯在哪個欄位、正確值應是什麼、依據來源是什麼"></textarea></div><div class="admin-actions"><button class="secondary-btn" type="button" onclick="submitIssueReport()">送出通報</button><button class="ghost-btn" type="button" onclick="closeIssueModal()">取消</button></div><div class="issue-form-note" id="${issueGithubLinkId()}">${escHtml(bridgeMessage)}</div></div>`;document.getElementById('issueModal').classList.add('open');}
function closeIssueModal(){document.getElementById('issueModal').classList.remove('open');}
async function submitIssueReport(){const drugId=document.getElementById(issueDrugId())?.value;const drug=findDrugById(_HD,drugId);if(!drug) return;const summary=(document.getElementById(issueSummaryId())?.value||'').trim();const details=(document.getElementById(issueDetailId())?.value||'').trim();if(!summary){alert('請先填寫摘要');return;}const form={field:(document.getElementById(issueFieldId())?.value||'other'),severity:(document.getElementById(issueSeverityId())?.value||'normal'),reporter:(document.getElementById(issueReporterId())?.value||'').trim(),source_url:(document.getElementById(issueSourceId())?.value||'').trim(),summary,details};let payload=buildIssuePayload(drug,form);if(issueBridgeState.available){try{const data=await issueBridgeRequest('/issues','POST',{title:buildIssueTitle(drug,payload),body:buildIssueBody(drug,payload),labels:buildIssueLabels(payload)});payload={...payload,github_issue_url:data.html_url||data.url||payload.github_issue_url,github_issue_number:data.number||null,github_issue_state:data.state||'open',sync_state:'created',last_sync_at:new Date().toISOString()};appendIssueTimeline(payload,{at:payload.last_sync_at,action:'issue_created',actor:payload.reporter||'reporter',note:`建立 GitHub issue #${payload.github_issue_number||''}`,status_to:payload.status});}catch(e){payload={...payload,sync_state:'error',last_sync_at:new Date().toISOString()};appendIssueTimeline(payload,{at:payload.last_sync_at,action:'issue_error',actor:payload.reporter||'reporter',note:e.message,status_to:payload.status});alert(`GitHub 開單失敗，已保留本機通報：${e.message}`);}}upsertLocalIssueReport(drug.id,payload);closeIssueModal();renderSidebar();renderCards();showDet(drug.id);}
function adminSelectId(drugId){return `adm-sel-${drugId}`;}
function adminVerifierId(drugId){return `adm-ver-${drugId}`;}
function adminNoteId(drugId){return `adm-note-${drugId}`;}
function adminCommandId(drugId){return `adm-cmd-${drugId}`;}
function getSelectedAdminFormulation(drugId){const drug=findDrugById(_HD,drugId);const select=document.getElementById(adminSelectId(drugId));if(!drug||!select) return null;return findFormulation(drug,select.value)||(drug.formulations||[])[0]||null;}
function refreshAdminCommand(drugId){const drug=findDrugById(_HD,drugId);const formulation=getSelectedAdminFormulation(drugId);const verifier=(document.getElementById(adminVerifierId(drugId))?.value||'').trim();const note=(document.getElementById(adminNoteId(drugId))?.value||'').trim();const out=document.getElementById(adminCommandId(drugId));if(!out) return;out.value=buildFormulationCommand(drug,formulation,verifier,note);}
function copyAdminCommand(drugId){const out=document.getElementById(adminCommandId(drugId));if(!out) return;out.select();out.setSelectionRange(0,out.value.length);if(navigator.clipboard?.writeText){navigator.clipboard.writeText(out.value).catch(()=>document.execCommand('copy'));}else{document.execCommand('copy');}}
function applyAdminFormulation(drugId){const raw=findDrugById(_RAW_HD,drugId);const selected=document.getElementById(adminSelectId(drugId));if(!raw||!selected) return;const verifier=(document.getElementById(adminVerifierId(drugId))?.value||'').trim();const note=(document.getElementById(adminNoteId(drugId))?.value||'').trim();const override={formulation_id:selected.value,verified_by:verifier,note,applied_at:new Date().toISOString()};adminOverrides[overrideKey(drugId)]=override;saveAdminOverrides();const idx=_HD.findIndex(x=>String(x.id)===String(drugId));if(idx>=0) _HD[idx]=buildDrugWithOverride(raw,override);renderSidebar();renderCards();showDet(drugId);}
function clearAdminFormulation(drugId){delete adminOverrides[overrideKey(drugId)];saveAdminOverrides();restoreDrugFromRaw(drugId);renderSidebar();renderCards();showDet(drugId);}
function renderFormulationAdmin(d){if((d.formulations?.length||0)<=1) return '';const local=d.local_admin_override;const manual=d.manual_review||{};const current=(d.formulations||[]).find(f=>f.is_primary) || d.formulations?.[0] || null;const statusTag=local?'<span class="src-tag src-local">本機已確認</span>':(manual.primary_formulation_confirmed?'<span class="src-tag src-nhi">已寫回主檔</span>':'<span class="src-tag src-tbd">待人工確認</span>');const statusText=local?'已在這個瀏覽器套用主劑型修正，但尚未寫回 JSON。':'請在下方選定主劑型，系統會立即更新畫面，並產生正式寫回主檔的指令。';const verifier=local?.verified_by||manual.verified_by||'';const note=local?.note||'';const options=(d.formulations||[]).map(f=>{const code=uniqueValues(f.nhi_drug_codes||[f.nhi_drug_code])[0]||'未標代碼';const price=typeof f.nhi_price==='number'?`NT$${f.nhi_price.toLocaleString()}`:'未標價';const ntuh=typeof f.ntuh_self_pay_price==='number'?`｜台大 NT$${f.ntuh_self_pay_price.toLocaleString()}`:'';return `<option value="${escAttr(f.formulation_id)}"${current?.formulation_id===f.formulation_id?' selected':''}>${escHtml(f.label||'未命名劑型')}｜${escHtml(code)}｜健保 ${escHtml(price)}${escHtml(ntuh)}</option>`;}).join('');const command=buildFormulationCommand(d,current,verifier,note);return `<div class="detail-section"><div class="section-hd"><span class="section-hd-label">人工確認工具</span>${statusTag}</div><div class="admin-panel"><div class="admin-status">${statusText}</div><div class="admin-grid"><div class="admin-field"><label for="${adminSelectId(d.id)}">主劑型</label><select class="admin-select" id="${adminSelectId(d.id)}" onchange="refreshAdminCommand(${d.id})">${options}</select></div><div class="admin-field"><label for="${adminVerifierId(d.id)}">確認者</label><input class="admin-input" id="${adminVerifierId(d.id)}" type="text" value="${escAttr(verifier)}" placeholder="例如 TH" oninput="refreshAdminCommand(${d.id})"></div></div><div class="admin-field"><label for="${adminNoteId(d.id)}">備註</label><textarea class="admin-note" id="${adminNoteId(d.id)}" placeholder="例如：改採院內常用 100mg/vial，台大與健保規格需分開看" oninput="refreshAdminCommand(${d.id})">${escHtml(note)}</textarea></div><div class="admin-field"><label for="${adminCommandId(d.id)}">正式寫回指令</label><textarea class="admin-command" id="${adminCommandId(d.id)}" readonly>${escHtml(command)}</textarea></div><div class="admin-actions"><button class="secondary-btn" type="button" onclick="applyAdminFormulation(${d.id})">套用本機確認</button><button class="copy-btn" type="button" onclick="copyAdminCommand(${d.id})">複製指令</button><button class="ghost-btn" type="button" onclick="clearAdminFormulation(${d.id})">清除本機確認</button></div><div class="admin-hint">本機確認只會存到這台裝置的瀏覽器。要同步到專案資料與 Git，請執行上方指令。</div></div></div>`;}
function renderCards(){const drugs=getFilt();document.getElementById('rCnt').textContent=`共 ${drugs.length} 種`;const grid=document.getElementById('cGrid');if(!drugs.length){grid.innerHTML='<div class="empty-state"><div class="empty-icon">&#128269;</div><p>找不到符合條件的藥物</p></div>';return;}grid.innerHTML=drugs.map(d=>{const dis=d.clinical_tags?.disease||[];const diT=dis.map(x=>`<span class="tag tag-disease">${dn(x)}</span>`).join('');const mT=molT(d);const aT=d.prior_auth?'<span class="tag tag-auth">事前審查</span>':'';const lT=`<span class="tag tag-line">L${d.therapy_line||1}</span>`;const localT=d.local_admin_override?'<span class="tag tag-mol">本機確認</span>':'';const pendingIssues=countPendingReports(d);const issueT=pendingIssues?`<span class="tag tag-warn">通報 ${pendingIssues}</span>`:'';const hasWarn=!!(d.data_note||d.manual_review?.multi_formulation_pending||pendingIssues);const warnT=hasWarn?'<span class="tag tag-warn">&#9888; 資料待確認</span>':'';const primaryPrice=primaryNhiPrice(d);const hasNhiPrice=typeof primaryPrice==='number';const isZeroNhiPrice=hasNhiPrice&&primaryPrice===0;const priceUnit=displayPriceUnit(d);const pT=hasNhiPrice?`健保藥價 <strong>NT$${primaryPrice.toLocaleString()}</strong>/<small>${priceUnit}</small>${isZeroNhiPrice?' <span class="tag tag-warn" style="margin-left:.3rem">0.00 待確認</span>':''}`:'';const issueBadge=pendingIssues?`<span class="issue-badge">待處理 ${pendingIssues}</span>`:'';return `<div class="drug-card" role="button" tabindex="0" onclick="showDet(${d.id})" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();showDet(${d.id});}"><div class="drug-card-header"><div class="drug-icon">${ini(d.generic_name)}</div><div><div class="drug-name">${d.generic_name}</div><div class="drug-trade">${d.trade_names||'(通用名)'}</div></div></div><div class="drug-tags">${diT}${mT}${aT}${lT}${warnT}${localT}${issueT}</div>${pT?`<div class="drug-price">${pT}</div>`:''}<div class="drug-card-actions"><div class="drug-card-hint">點擊查看詳細資料</div><div style="display:flex;align-items:center;gap:.45rem">${issueBadge}<button class="mini-btn issue" type="button" onclick="event.stopPropagation();openIssueReporter(${d.id})">錯誤通報</button></div></div></div>`;}).join('');}
function getUMg(pu){const m=(pu||'').match(/(\d+(?:\.\d+)?)\s*mg/i);return m?parseFloat(m[1]):1;}
function showDet(id){
  const d=_HD.find(x=>x.id===id);
  if(!d) return;
  let nfo=null;
  try{nfo=typeof d.dosage_info==='string'?JSON.parse(d.dosage_info):d.dosage_info;}catch(e){}
  const dis=d.clinical_tags?.disease||[];
  const mols=[];
  if(d.clinical_tags?.btk) mols.push('BTK抑制劑');
  if(d.clinical_tags?.cd20) mols.push('Anti-CD20');
  if(d.clinical_tags?.flt3) mols.push('FLT3抑制劑');
  if(d.clinical_tags?.ph_positive) mols.push('Ph+/BCR-ABL適用');
  if(d.clinical_tags?.bcl2) mols.push('BCL-2抑制劑');
  const rmap={'oral':'口服','iv':'靜脈注射','sc':'皮下注射','sc_iv':'皮下/靜脈','oral_or_iv':'口服或靜脈'};
  const route=rmap[nfo?.type]||'';
  const indic=(d.indication||'').split('|').map(s=>s.trim()).filter(Boolean);
  const conds=(d.conditions||'').split('|').map(s=>s.trim()).filter(Boolean);
  const priceUnit=displayPriceUnit(d);
  const uMg=getUMg(priceUnit);
  const primaryPrice=primaryNhiPrice(d);
  const p=primaryPrice||0;
  const hasNhiPrice=typeof primaryPrice==='number';
  const isZeroNhiPrice=hasNhiPrice&&primaryPrice===0;
  const srcLine=lineSrcTag(d.therapy_line_source||'待確認');
  const nhiDate=fmtRocDate(primaryEffectiveDate(d))||'115/05/06';
  const nhiSourceUrl=(d.nhi_pay_pdf_urls||[])[0] || (d.nhi_open_data?.dataset_identifier ? `https://info.nhi.gov.tw/api/iode0010/v1/rest/dataset/${d.nhi_open_data.dataset_identifier}` : '');
  const nhiDateTag=linkTag(nhiSourceUrl, `健保生效 ${nhiDate}`, 'src-nhi');
  const ntuhDate=fmtIsoDate(d.ntuh_open_data?.query_date);
  const ntuhDateTag=ntuhDate?` ${linkTag(d.ntuh_open_data?.source_url, `台大查詢 ${ntuhDate}`, 'src-nccn')}`:'';
  const ntuhPrice=(typeof d.ntuh_self_pay_price==='number'&&d.ntuh_self_pay_price>0)?d.ntuh_self_pay_price:null;
  const ntuhPriceUnit=d.ntuh_price_unit||priceUnit;
  const ntuhPriceHtml=ntuhPrice?`<strong>NT$${ntuhPrice.toLocaleString()}</strong> / ${ntuhPriceUnit}`:'<span style="color:var(--text-muted);font-size:.78rem">尚未建檔</span>';
  const ntuhMeta=d.ntuh_open_data?.selected_product_name?`<div style="font-size:.76rem;color:var(--text-muted);margin-top:.2rem">${d.ntuh_open_data.selected_product_name}</div>`:'';
  const ntuhNhiHtml=d.ntuh_open_data?.selected_nhi_price_text?`<div style="font-size:.76rem;color:var(--text-muted);margin-top:.2rem">台大頁面健保價：${d.ntuh_open_data.selected_nhi_price_text}</div>`:'';
  const recommendationHtml=renderRecommendationSources(d);
  const recordHtml=renderRecordVersions(d);
  const issueHtml=renderIssueTracking(d);
  const reviewHtml=renderReviewSupport(d);
  const adminHtml=renderFormulationAdmin(d);
  const formulationWarn=formulationWarnText(d);
  const warnParts=[];
  if(d.data_note) warnParts.push(`<div><strong>資料缺漏警告</strong>${d.data_note}</div>`);
  if(formulationWarn) warnParts.push(`<div><strong>多劑型人工確認</strong>${formulationWarn}</div>`);
  if(d.local_admin_override) warnParts.push('<div><strong>本機確認尚未寫回</strong>此瀏覽器已套用主劑型修正；若要同步到專案資料，請執行下方正式寫回指令。</div>');
  if(hasPendingReports(d)) warnParts.push('<div><strong>錯誤通報待確認</strong>這個藥物目前已有待處理通報，請先核對詳細頁中的錯誤通報紀錄。</div>');
  const formulations=(d.formulations||[]).map(f=>{
    const activeTag=f.is_primary?'<span class="src-tag src-nhi">主劑型</span>':'';
    const priceText=typeof f.nhi_price==='number'?`NT$${f.nhi_price.toLocaleString()} / ${f.label||'unit'}`:`${f.label||'unit'}`;
    const codeList=(f.nhi_drug_codes||[]).filter(Boolean);
    const codeText=codeList.length?`<div style="font-size:.74rem;color:var(--text-muted)">藥品代碼：${codeList.join('、')}</div>`:(f.nhi_drug_code?`<div style="font-size:.74rem;color:var(--text-muted)">藥品代碼：${f.nhi_drug_code}</div>`:'');
    const matchText=(f.matched_row_count&&f.matched_row_count>1)?`<div style="font-size:.74rem;color:var(--text-muted)">官方對應紀錄：${f.matched_row_count} 筆</div>`:'';
    const ntuhText=typeof f.ntuh_self_pay_price==='number'?`<div style="font-size:.74rem;color:var(--text-muted)">台大自費價：NT$${f.ntuh_self_pay_price.toLocaleString()} / ${f.label||'unit'}</div>`:'';
    return `<li><strong>${priceText}</strong> ${activeTag}${codeText}${matchText}${ntuhText}</li>`;
  }).join('');
  const formulationsHtml=(d.formulations?.length||0)>0?`<div class="detail-section"><div class="section-hd"><span class="section-hd-label">劑型確認</span><span class="src-tag ${d.manual_review?.multi_formulation_pending?'src-tbd':'src-nhi'}">${d.manual_review?.multi_formulation_pending?'待人工確認':'已建主劑型'}</span></div><ul class="cond-list">${formulations}</ul></div>`:'';
  const warnBox=warnParts.length?`<div class="data-warn">${warnParts.join('')}</div>`:'';
  let cHtml='';
  if(nfo?.dose_per_bsa){
    const defDays=nfo.schedule?parseInt(nfo.schedule):1;
    cHtml=`<div class="calc-box"><div class="calc-title">&#128176; 費用試算（每療程周期） <span style="font-size:.7rem;font-weight:400;color:var(--heme-light)">來源：健保藥價基準 115/5/6</span></div><div class="calc-row"><span class="calc-label">BSA</span><input class="calc-input" id="cB${id}" type="number" value="1.7" step="0.1" min="0.5" max="3"><span class="calc-unit">m²</span></div><div class="calc-row"><span class="calc-label">劑量</span><input class="calc-input" id="cD${id}" type="number" value="${nfo.dose_per_bsa}" step="1"><span class="calc-unit">${nfo.unit||'mg/m²'}</span></div><div class="calc-row"><span class="calc-label">天數</span><input class="calc-input" id="cDy${id}" type="number" value="${defDays}" step="1" min="1"><span class="calc-unit">天/周期</span></div><div class="calc-bonus-wrap"><label class="calc-bonus-toggle"><input type="checkbox" id="bOn${id}" onchange="toggleBonus(${id})"> 贈藥方案</label><div class="calc-bonus-panel" id="bp${id}" style="display:none"><div class="calc-row"><span class="calc-label">模式</span><select class="calc-select" id="bMode${id}" onchange="toggleBonusMode(${id})"><option value="cycle">依週期贈N瓶</option><option value="buyn">買N送1</option></select></div><div id="bCycleRow${id}" class="calc-row"><span class="calc-label">每週期贈</span><input class="calc-input" id="bVal${id}" type="number" value="1" min="0" step="1" style="width:5rem"><span class="calc-unit">瓶/粒</span></div><div id="bBuynRow${id}" class="calc-row" style="display:none"><span class="calc-label">買</span><input class="calc-input" id="bN${id}" type="number" value="10" min="2" step="1" style="width:5rem"><span class="calc-unit">送 1</span></div></div></div><button class="calc-btn" onclick="cBSA(${id},${p},${uMg})">計算</button><div id="cR${id}" class="calc-result" style="display:none"></div></div>`;
  } else if(nfo?.dose_per_kg){
    cHtml=`<div class="calc-box"><div class="calc-title">&#128176; 費用試算（每次給藥） <span style="font-size:.7rem;font-weight:400;color:var(--heme-light)">來源：健保藥價基準 115/5/6</span></div><div class="calc-row"><span class="calc-label">體重</span><input class="calc-input" id="cW${id}" type="number" value="60" step="1"><span class="calc-unit">kg</span></div><div class="calc-row"><span class="calc-label">劑量</span><input class="calc-input" id="cKD${id}" type="number" value="${nfo.dose_per_kg}" step="0.1"><span class="calc-unit">${nfo.unit||'mg/kg'}</span></div><div class="calc-bonus-wrap"><label class="calc-bonus-toggle"><input type="checkbox" id="bOn${id}" onchange="toggleBonus(${id})"> 贈藥方案</label><div class="calc-bonus-panel" id="bp${id}" style="display:none"><div class="calc-row"><span class="calc-label">模式</span><select class="calc-select" id="bMode${id}" onchange="toggleBonusMode(${id})"><option value="cycle">依週期贈N瓶</option><option value="buyn">買N送1</option></select></div><div id="bCycleRow${id}" class="calc-row"><span class="calc-label">每週期贈</span><input class="calc-input" id="bVal${id}" type="number" value="1" min="0" step="1" style="width:5rem"><span class="calc-unit">瓶/粒</span></div><div id="bBuynRow${id}" class="calc-row" style="display:none"><span class="calc-label">買</span><input class="calc-input" id="bN${id}" type="number" value="10" min="2" step="1" style="width:5rem"><span class="calc-unit">送 1</span></div></div></div><button class="calc-btn" onclick="cKG(${id},${p},${uMg})">計算</button><div id="cR${id}" class="calc-result" style="display:none"></div></div>`;
  } else if(nfo?.dose_fixed){
    const defD=nfo.schedule?parseInt(nfo.schedule):28;
    cHtml=`<div class="calc-box"><div class="calc-title">&#128176; 費用試算（口服療程） <span style="font-size:.7rem;font-weight:400;color:var(--heme-light)">來源：健保藥價基準 115/5/6</span></div><div class="calc-row"><span class="calc-label">每日劑量</span><input class="calc-input" id="cFD${id}" type="number" value="${nfo.dose_fixed}" step="1"><span class="calc-unit">${nfo.unit||'mg'}/日</span></div><div class="calc-row"><span class="calc-label">天數</span><input class="calc-input" id="cFDy${id}" type="number" value="${defD}" step="1" min="1"><span class="calc-unit">天</span></div><div class="calc-bonus-wrap"><label class="calc-bonus-toggle"><input type="checkbox" id="bOn${id}" onchange="toggleBonus(${id})"> 贈藥方案</label><div class="calc-bonus-panel" id="bp${id}" style="display:none"><div class="calc-row"><span class="calc-label">模式</span><select class="calc-select" id="bMode${id}" onchange="toggleBonusMode(${id})"><option value="cycle">依週期贈N瓶</option><option value="buyn">買N送1</option></select></div><div id="bCycleRow${id}" class="calc-row"><span class="calc-label">每週期贈</span><input class="calc-input" id="bVal${id}" type="number" value="1" min="0" step="1" style="width:5rem"><span class="calc-unit">瓶/粒</span></div><div id="bBuynRow${id}" class="calc-row" style="display:none"><span class="calc-label">買</span><input class="calc-input" id="bN${id}" type="number" value="10" min="2" step="1" style="width:5rem"><span class="calc-unit">送 1</span></div></div></div><button class="calc-btn" onclick="cFix(${id},${p},${uMg})">計算</button><div id="cR${id}" class="calc-result" style="display:none"></div></div>`;
  }
  document.getElementById('detC').innerHTML=`<div class="modal-header"><div class="modal-icon">${ini(d.generic_name)}</div><div style="flex:1"><div class="modal-title">${d.generic_name}</div><div class="modal-subtitle">${d.trade_names||'(通用名)'} &middot; ${dis.map(x=>dn(x)).join('/')}</div></div><button class="modal-close" onclick="closeDet()">&#x2715;</button></div><div class="modal-body">${warnBox}<div class="detail-section"><dl><div class="detail-row"><dt>適用疾病</dt><dd>${dis.map(x=>dn(x)).join('、')||'—'}</dd></div>${mols.length?`<div class="detail-row"><dt>分子標記</dt><dd>${mols.join('、')}</dd></div>`:''}<div class="detail-row"><dt>治療線</dt><dd>第 ${d.therapy_line||1} 線 ${srcLine}</dd></div><div class="detail-row"><dt>健保審查</dt><dd>${d.prior_auth?'<span style="color:var(--auth)">&#9888; 需事前審查</span>':'<span style="color:var(--nhi)">&#10003; 免事前審查</span>'}</dd></div>${route?`<div class="detail-row"><dt>給藥途徑</dt><dd>${route}</dd></div>`:''}${nfo?.note?`<div class="detail-row"><dt>建議劑量</dt><dd>${nfo.note}</dd></div>`:''}<div class="detail-row"><dt>健保單價</dt><dd><strong>NT$${p.toLocaleString()}</strong> / ${priceUnit} ${nhiDateTag}${isZeroNhiPrice?' <span class="src-tag src-tbd">官方回傳 0.00，待人工確認</span>':''}</dd></div><div class="detail-row"><dt>台大院內自費價</dt><dd>${ntuhPriceHtml}${ntuhDateTag}${ntuhMeta}${ntuhNhiHtml}</dd></div></dl></div><hr class="detail-divider">${indic.length?`<div class="detail-section"><div class="section-hd"><span class="section-hd-label">健保給付適應症</span><span class="src-tag src-nhi">全民健康保險藥物給付項目及支付標準</span></div><ul class="cond-list">${indic.map(l=>`<li>${l}</li>`).join('')}</ul></div>`:''}${conds.length?`<div class="detail-section"><div class="section-hd"><span class="section-hd-label">給付條件 / 事前審查要點</span><span class="src-tag src-nhi">全民健康保險藥物給付項目及支付標準</span></div><ul class="cond-list">${conds.map(l=>`<li>${l}</li>`).join('')}</ul></div>`:''}${issueHtml}${recommendationHtml}${recordHtml}${formulationsHtml}${adminHtml}${reviewHtml}${cHtml}</div>`;
  document.getElementById('detModal').classList.add('open');
  initReviewSupport(d);
  if((d.formulations?.length||0)>1) refreshAdminCommand(d.id);
}
function closeDet(){document.getElementById('detModal').classList.remove('open');}
function getBonusSettings(id){const on=document.getElementById('bOn'+id);if(!on||!on.checked) return null;const mode=document.getElementById('bMode'+id)?.value||'cycle';const val=+(document.getElementById('bVal'+id)?.value||1);const n=+(document.getElementById('bN'+id)?.value||10);return {mode,val:mode==='cycle'?val:n};}
function toggleBonus(id){const on=document.getElementById('bOn'+id)?.checked;const panel=document.getElementById('bp'+id);if(panel) panel.style.display=on?'':'none';}
function toggleBonusMode(id){const mode=document.getElementById('bMode'+id)?.value;const cr=document.getElementById('bCycleRow'+id);const br=document.getElementById('bBuynRow'+id);if(cr) cr.style.display=mode==='cycle'?'':'none';if(br) br.style.display=mode==='buyn'?'':'none';}
function showRes(id,tot,units,p,cost){const el=document.getElementById('cR'+id);if(!el) return;const bonus=getBonusSettings(id);let bonusHtml='';if(bonus){let pu,pc;if(bonus.mode==='cycle'){pu=Math.max(0,units-bonus.val);pc=pu*p;bonusHtml=`<div class="calc-bonus-result">贈藥折扣：每週期贈 ${bonus.val} 瓶/粒 → 實付 ${pu} 瓶/粒 = <strong>NT$${pc.toLocaleString()}</strong></div>`;}else{const g=bonus.val+1;const fg=Math.floor(units/g);const rm=units%g;pu=fg*bonus.val+rm;pc=pu*p;bonusHtml=`<div class="calc-bonus-result">贈藥折扣：買 ${bonus.val} 送 1 → 實付 ${pu} 瓶/粒 = <strong>NT$${pc.toLocaleString()}</strong></div>`;}}el.style.display='block';el.innerHTML=`總量 ${tot.toFixed(0)} mg &#8594; ${units} 瓶/粒 &#215; NT$${p.toLocaleString()} = <span>NT$${cost.toLocaleString()}</span>${bonusHtml}`;}
function cBSA(id,p,uMg){const bsa=+document.getElementById('cB'+id).value||1.7;const dose=+document.getElementById('cD'+id).value||0;const days=+document.getElementById('cDy'+id).value||1;const tot=dose*bsa*days;const v=Math.ceil(tot/uMg);showRes(id,tot,v,p,v*p);}
function cKG(id,p,uMg){const wt=+document.getElementById('cW'+id).value||60;const dose=+document.getElementById('cKD'+id).value||0;const tot=dose*wt;const v=Math.ceil(tot/uMg);showRes(id,tot,v,p,v*p);}
function cFix(id,p,uMg){const daily=+document.getElementById('cFD'+id).value||0;const days=+document.getElementById('cFDy'+id).value||28;const tot=daily*days;const v=Math.ceil(tot/uMg);showRes(id,tot,v,p,v*p);}
function showCL(){document.getElementById('clModal').classList.add('open');}
function closeCL(){document.getElementById('clModal').classList.remove('open');}
document.addEventListener('DOMContentLoaded',async()=>{adminOverrides=loadAdminOverrides();localIssueReports=normalizeIssueReportStore(loadIssueReports());applyStoredOverrides();await detectIssueBridge();renderSidebar();renderCards();});
"""


def build_site(
    *,
    drugs: list[dict],
    site_config: dict,
    output_html_path: str | Path,
    output_json_path: str | Path,
) -> str:
    inline_json = json.dumps(drugs, ensure_ascii=False, separators=(",", ":"))
    Path(output_json_path).write_text(json.dumps(drugs, ensure_ascii=False, indent=2), encoding="utf-8")
    js = JS_TEMPLATE.replace("DRUGDATA", inline_json)
    js = js.replace("__PROJECT_REPO_URL__", site_config.get("project_repo_url", ""))
    js = js.replace("__ISSUE_NEW_URL__", site_config.get("github_issue_new_url", ""))
    js = js.replace("__ISSUE_BRIDGE_URL__", site_config.get("issue_bridge_url", ""))
    changelog_html = site_config.get("changelog_html", "")
    project_repo_url = site_config.get("project_repo_url", "")
    project_link_html = (
        f'<a class="header-link" href="{project_repo_url}" target="_blank" rel="noopener noreferrer">GitHub</a>'
        if project_repo_url
        else ""
    )
    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{site_config['html_title']}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header class="header">
  <div>
    <div class="header-title">&#129978; {site_config['header_title']}</div>
    <div class="header-sub">{site_config['header_subtitle']}</div>
  </div>
  <div class="header-actions">
    {project_link_html}
    <div class="header-badge" onclick="showCL()">{site_config['price_basis_label']} &#65372; {site_config['version_label']}</div>
  </div>
</header>
<div class="mobile-filter-bar" id="mobFilt"></div>
<div class="layout">
  <aside class="sidebar">
    <div class="sidebar-section"><div class="sidebar-label">疾病分類</div><div id="dFilt"></div></div>
    <div class="sidebar-section"><div class="sidebar-label">分子標記</div><div class="mol-filter" id="mFilt"></div></div>
    <div class="sidebar-section"><div class="sidebar-label">治療線</div><div id="lFilt"></div></div>
  </aside>
  <main class="main">
    <div class="search-wrap">
      <input class="search-input" type="text" id="sIn" placeholder="搜尋藥物名稱、適應症..." oninput="renderCards()">
      <span class="result-count" id="rCnt"></span>
    </div>
    <div class="cards-grid" id="cGrid"></div>
  </main>
</div>
<div class="modal-overlay" id="detModal" onclick="if(event.target===this)closeDet()"><div class="modal" id="detC"></div></div>
<div class="modal-overlay" id="issueModal" onclick="if(event.target===this)closeIssueModal()"><div class="modal" id="issueC"></div></div>
<div class="modal-overlay" id="clModal" onclick="if(event.target===this)closeCL()">
  <div class="modal">
    <div class="modal-header">
      <div class="modal-icon">&#128203;</div>
      <div><div class="modal-title">版本更新紀錄</div><div class="modal-subtitle">Changelog</div></div>
      <button class="modal-close" onclick="closeCL()">&#x2715;</button>
    </div>
    <div class="modal-body">{changelog_html}</div>
  </div>
</div>
<script>{js}</script>
</body>
</html>"""
    Path(output_html_path).write_text(html, encoding="utf-8")
    return html

SITE_CONFIG = {
    "specialty_id": "oncology_heme",
    "html_title": "健保血液腫瘤藥物查詢系統",
    "header_title": "健保血液腫瘤藥物查詢",
    "header_subtitle": "Hematology Oncology NHI Drug Reference ｜ 57 種藥物",
    "version_label": "v1.2",
    "price_basis_label": "藥價基準 115/05/06",
    "project_repo_url": "https://github.com/erichuang777777/NHI_Drug_Caculator",
    "github_issue_new_url": "https://github.com/erichuang777777/NHI_Drug_Caculator/issues/new",
    "issue_bridge_url": "http://127.0.0.1:8765",
    "default_source_data": "data/heme_drugs_clean.json",
    "default_output_json": "data/heme_final.json",
    "default_output_html": "index.html",
    "changelog_html": """
      <div class="cl-version">
        <div class="cl-ver-badge">v1.2 &#8212; 2026/05</div>
        <ul class="cl-items">
          <li>新增 27 種血液腫瘤藥物（MF、ET、PV、PCNSL、DLBCL、FL、MCL、WM、ITP/AA、T細胞淋巴瘤、HL、MCD），共收錄 57 種</li>
          <li>費用試算器新增贈藥方案功能：支援「依週期贈N瓶」與「買N送1」兩種模式，自動計算實際給付費用</li>
          <li>更新健保藥價基準日期至 115/05/06</li>
        </ul>
      </div>
      <div class="cl-version">
        <div class="cl-ver-badge">v1.1 &#8212; 2026/04</div>
        <ul class="cl-items">
          <li>資料完整性政策：所有欄位必須附帶來源標籤（健保規定 / NCCN / 待確認）</li>
          <li>新增台大醫院院內自費價同步欄位，並獨立顯示台大查詢日期與台大頁面健保價</li>
          <li>新增「審查資料整理」區塊：可輸入 CLL、AML、MDS、WM、FL 常見送審欄位並自動產生摘要</li>
          <li>移除虛構的適應症文字（Dexamethasone、Doxorubicin、Rituximab、Thalidomide、Oxaliplatin）</li>
          <li>新增「資料缺漏警告」標示，明確說明哪些藥品的健保登載文字不符血液腫瘤科適應症</li>
          <li>治療線校正（依健保給付規定文字）：Brentuximab vedotin L2&#8594;L1；Carfilzomib L1&#8594;L2；Elotuzumab L1&#8594;L3；Pomalidomide L1&#8594;L3</li>
          <li>治療線來源標籤校正：骨幹化療藥物（Cyclophosphamide、Dexamethasone、Doxorubicin、Oxaliplatin、Vinblastine）標記 NCCN；Rituximab、Thalidomide 標記「待確認」</li>
          <li>費用試算器顯示健保藥價基準日期（115/04/01）</li>
        </ul>
      </div>
      <div class="cl-version">
        <div class="cl-ver-badge">v1.0 &#8212; 2026/04</div>
        <ul class="cl-items">
          <li>建立血液腫瘤藥物獨立查詢系統（獨立部署）</li>
          <li>收錄 30 種血液腫瘤常用藥物（健保給付），已去除品牌名重複條目</li>
          <li>疾病分類篩選：CLL、淋巴瘤、多發性骨髓瘤、CML、AML、MDS、ALL</li>
          <li>分子標記篩選：BTK抑制劑、Anti-CD20、FLT3、Ph+/BCR-ABL、BCL-2</li>
          <li>藥物翻轉卡片 + 詳細資料 Modal + 費用試算器</li>
          <li>健保藥價資料：115/04/01 公告</li>
        </ul>
      </div>
    """,
}

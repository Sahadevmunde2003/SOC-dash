import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, AlertOctagon, ArrowDownRight, ArrowUpRight, Bell, CheckCircle2, ChevronRight, CircleHelp, Clock3, Command, Database, Download, Filter, Globe2, LayoutDashboard, ListFilter, LockKeyhole, Menu, Network, RefreshCw, Search, Server, Shield, ShieldAlert, ShieldCheck, Siren, TerminalSquare, X } from 'lucide-react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import './styles.css';

const API = 'http://127.0.0.1:5000/api';
const activityData = [
  {time:'00:00', alerts:8}, {time:'04:00', alerts:5}, {time:'08:00', alerts:17},
  {time:'12:00', alerts:12}, {time:'16:00', alerts:29}, {time:'20:00', alerts:21}
];
const fallbackAlerts = [
  {id:'SOC-2026-1042',title:'Repeated SSH authentication failures',severity:'High',status:'New',source:'Ubuntu auth',src_ip:'192.0.2.24',dst_ip:'10.10.20.10',timestamp:'2026-10-18T13:02:00Z',technique:'T1110',technique_name:'Brute Force',description:'Multiple failed SSH logins observed in the sample authentication log.',evidence:['8 failed login attempts in 2 minutes','Account: labuser','Sensor: ubuntu-dmz']},
  {id:'SOC-2026-1043',title:'Suspicious phishing URL',severity:'Critical',status:'Investigating',source:'Email analysis',src_ip:'198.51.100.18',dst_ip:'10.10.10.25',timestamp:'2026-10-18T12:44:00Z',technique:'T1566.002',technique_name:'Spearphishing Link',description:'A sample email contains a mismatched sender display name and an obfuscated URL.',evidence:['SPF: fail (sample result)','URL host differs from displayed link','IOC reputation: not checked']},
  {id:'SOC-2026-1044',title:'Unusual outbound connection',severity:'Medium',status:'New',source:'pfSense firewall',src_ip:'10.10.20.15',dst_ip:'203.0.113.42',timestamp:'2026-10-18T12:18:00Z',technique:'T1071.001',technique_name:'Web Protocols',description:'A synthetic firewall event records an outbound HTTPS connection requiring analyst review.',evidence:['Protocol: TCP','Destination port: 443','Disposition: pass']},
  {id:'SOC-2026-1045',title:'Multiple blocked inbound probes',severity:'Low',status:'Closed',source:'pfSense firewall',src_ip:'198.51.100.77',dst_ip:'10.10.20.10',timestamp:'2026-10-18T11:58:00Z',technique:'T1046',technique_name:'Network Service Discovery',description:'Sample firewall records show several blocked connection attempts.',evidence:['Action: block','Destination ports: 22, 80, 443','No confirmed compromise']},
  {id:'SOC-2026-1046',title:'New admin group membership',severity:'High',status:'Investigating',source:'Endpoint sample',src_ip:'10.10.20.21',dst_ip:'10.10.20.21',timestamp:'2026-10-18T10:36:00Z',technique:'T1098',technique_name:'Account Manipulation',description:'Simulated endpoint event indicates a privileged group membership change.',evidence:['Event type: group membership change','Host: lab-windows-01','User: demo-admin']}
];
const fmtTime = (value) => { try { return new Date(value).toLocaleString([], {month:'short',day:'2-digit',hour:'2-digit',minute:'2-digit'}); } catch { return value; } };
function App() {
  const [alerts, setAlerts] = useState(fallbackAlerts);
  const [summary, setSummary] = useState({total_alerts:5,open_incidents:4,critical_alerts:1,investigating:2,severity_counts:{Critical:1,High:2,Medium:1,Low:1}});
  const [apiOnline, setApiOnline] = useState(false);
  const [query, setQuery] = useState('');
  const [severity, setSeverity] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [selected, setSelected] = useState(null);
  const [page, setPage] = useState('Overview');
  const [notice, setNotice] = useState('');
  const [loading, setLoading] = useState(false);
  async function loadData() {
    setLoading(true);
    try {
      const [healthRes, summaryRes, alertsRes] = await Promise.all([fetch(API+'/health'), fetch(API+'/summary'), fetch(API+'/alerts')]);
      if (!healthRes.ok || !summaryRes.ok || !alertsRes.ok) throw new Error('API unavailable');
      const [health, sum, alertBody] = await Promise.all([healthRes.json(), summaryRes.json(), alertsRes.json()]);
      setApiOnline(health.status === 'ok'); setSummary(sum); setAlerts(alertBody.items || []);
    } catch { setApiOnline(false); }
    finally { setLoading(false); }
  }
  useEffect(() => { loadData(); }, []);
  const visibleAlerts = useMemo(() => alerts.filter(a => {
    const haystack = [a.id,a.title,a.source,a.src_ip,a.dst_ip,a.technique,a.technique_name].join(' ').toLowerCase();
    return (!query || haystack.includes(query.toLowerCase())) && (severity === 'All' || a.severity === severity) && (statusFilter === 'All' || a.status === statusFilter);
  }), [alerts, query, severity, statusFilter]);
  async function changeStatus(alert, status) {
    try {
      const res = await fetch(API+'/alerts/'+encodeURIComponent(alert.id)+'/status', {method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({status})});
      if (!res.ok) throw new Error();
      const updated = await res.json();
      setAlerts(old => old.map(a => a.id === updated.id ? updated : a));
      setSelected(updated); setNotice('Incident status updated'); setTimeout(() => setNotice(''), 2500);
      loadData();
    } catch { setNotice('Could not update status. Start the Flask API first.'); setTimeout(() => setNotice(''), 3500); }
  }
  function exportAlerts() {
    const blob = new Blob([JSON.stringify(visibleAlerts,null,2)], {type:'application/json'});
    const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href=url; a.download='sentinel-soc-alerts.json'; a.click(); URL.revokeObjectURL(url);
  }
  const nav = [
    {name:'Overview',icon:LayoutDashboard},{name:'Alerts',icon:ShieldAlert,count:visibleAlerts.length},
    {name:'Incidents',icon:Siren},{name:'Threat intelligence',icon:Globe2},
    {name:'Network events',icon:Network},{name:'Detection rules',icon:ListFilter},
    {name:'MITRE ATT&CK',icon:Command},{name:'Reports',icon:Download}
  ];
  const severityClass = (s) => 'severity severity-'+(s||'Low').toLowerCase();
  const statusClass = (s) => 'status status-'+(s||'New').toLowerCase().replace(' ','-');
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><ShieldCheck size={22}/></div><div><strong>SENTINEL<span> SOC</span></strong><small>SECURITY OPERATIONS</small></div></div>
      <div className="workspace-label">WORKSPACE <span className="live-dot"/></div>
      <div className="workspace"><div className="workspace-icon">L</div><div><b>Lab environment</b><small>Personal SOC workspace</small></div><ChevronRight size={15}/></div>
      <div className="nav-label">MONITOR</div>
      <nav>{nav.map(item => <button key={item.name} className={'nav-item '+(page===item.name?'active':'')} onClick={()=>setPage(item.name)}><item.icon size={17}/><span>{item.name}</span>{item.count!==undefined&&<em>{item.count}</em>}</button>)}</nav>
      <div className="sidebar-bottom"><div className="sensor-card"><div className="sensor-head"><span className={'sensor-status '+(apiOnline?'online':'')}/><b>Event pipeline</b><span className="sensor-label">{apiOnline?'ONLINE':'DEMO'}</span></div><p>{apiOnline?'Flask API connected':'Using bundled sample events'}</p><div className="sensor-track"><span style={{width:apiOnline?'100%':'62%'}}/></div><small>{apiOnline?'API responding':'Local demo mode'}</small></div><button className="nav-item" onClick={()=>setNotice('Settings panel is planned for a future milestone.')}><CircleHelp size={17}/><span>Help & settings</span></button><div className="user-row"><div className="avatar">SA</div><div><b>SOC Analyst</b><small>Tier 1 · Lab</small></div><span className="user-menu">•••</span></div></div>
    </aside>
    <main className="main-area">
      <header className="topbar"><div className="breadcrumb"><span>Workspace</span><ChevronRight size={14}/><b>{page}</b></div><div className="top-actions"><div className="environment"><span className="live-dot"/> LAB ENVIRONMENT</div><button className="icon-button" title="Refresh data" onClick={loadData}><RefreshCw size={17} className={loading?'spin':''}/></button><button className="icon-button notification" title="Notifications" onClick={()=>setNotice('No new system notifications.')}><Bell size={17}/><i/></button><div className="top-avatar">SA</div></div></header>
      <div className="content">
        <section className="welcome-row"><div><div className="eyebrow"><span className="pulse"/> SECURITY OPERATIONS CENTER <span className="eyebrow-divider">/</span> <span className="muted">OVERVIEW</span></div><h1>{page==='Overview'?'Security overview':page}</h1><p className="subtitle">Monitor detections, triage alerts, and investigate suspicious activity across your lab.</p></div><div className="welcome-actions"><button className="button secondary" onClick={exportAlerts}><Download size={15}/> Export JSON</button><button className="button primary" onClick={()=>{setPage('Alerts');setSelected(visibleAlerts[0]||null)}}><Shield size={15}/> Open alert queue</button></div></section>
        <div className="demo-banner"><div className="banner-icon"><Activity size={16}/></div><div><b>{apiOnline?'API connected · Lab telemetry ready':'Demo data mode'}</b><span>{apiOnline?'Connected to the local Flask API. Events are currently stored in memory.':'Synthetic events are displayed for demonstration. Connect your own authorized lab log sources for live telemetry.'}</span></div><span className="demo-tag">{apiOnline?'CONNECTED':'SIMULATED'}</span></div>
        <section className="metric-grid">
          <Metric icon={Activity} label="Total alerts" value={summary.total_alerts ?? alerts.length} note="Events in current dataset" accent="blue" trend="LIVE DATASET"/>
          <Metric icon={AlertOctagon} label="Critical alerts" value={summary.critical_alerts ?? alerts.filter(a=>a.severity==='Critical').length} note="Prioritize for triage" accent="red" trend="HIGH PRIORITY"/>
          <Metric icon={Siren} label="Open incidents" value={summary.open_incidents ?? alerts.filter(a=>a.status!=='Closed').length} note="Not yet closed" accent="amber" trend="IN PROGRESS"/>
          <Metric icon={Clock3} label="Investigating" value={summary.investigating ?? alerts.filter(a=>a.status==='Investigating').length} note="Active analyst reviews" accent="violet" trend="ANALYST QUEUE"/>
        </section>
        <section className="dashboard-grid">
          <div className="panel chart-panel"><div className="panel-heading"><div><h2>Alert activity</h2><p>Event volume across the last 24 hours</p></div><button className="period-select" onClick={()=>setNotice('Chart currently uses illustrative hourly sample data.')}>Last 24 hours <ChevronRight size={13}/></button></div><div className="chart-legend"><span><i/> Alert volume</span><span className="chart-caption">ILLUSTRATIVE DATA</span></div><div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><AreaChart data={activityData} margin={{top:12,right:8,left:-18,bottom:0}}><defs><linearGradient id="alertFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#38bdf8" stopOpacity={0.28}/><stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/></linearGradient></defs><CartesianGrid stroke="#202c3d" strokeDasharray="3 5" vertical={false}/><XAxis dataKey="time" tick={{fill:'#73839a',fontSize:11}} axisLine={false} tickLine={false}/><YAxis tick={{fill:'#73839a',fontSize:11}} axisLine={false} tickLine={false}/><Tooltip contentStyle={{background:'#101a29',border:'1px solid #28384d',borderRadius:10,color:'#e7eef8'}}/><Area type="monotone" dataKey="alerts" stroke="#38bdf8" strokeWidth={2.5} fill="url(#alertFill)" activeDot={{r:5,fill:'#38bdf8',stroke:'#0c1523',strokeWidth:2}}/></AreaChart></ResponsiveContainer></div></div>
          <div className="panel severity-panel"><div className="panel-heading"><div><h2>Severity breakdown</h2><p>Alerts by priority</p></div><button className="small-icon" onClick={()=>{setPage('Alerts');setSeverity('All')}}><ChevronRight size={17}/></button></div><div className="severity-list">{['Critical','High','Medium','Low'].map(s=>{const n=(summary.severity_counts||{})[s] ?? alerts.filter(a=>a.severity===s).length;const pct=Math.max(3,Math.round(n/Math.max(1,summary.total_alerts||alerts.length)*100));return <button className="severity-row" key={s} onClick={()=>{setSeverity(s);setPage('Alerts')}}><div className="severity-label"><span className={'severity-dot dot-'+s.toLowerCase()}/><span>{s}</span><b>{n}</b></div><div className="bar-track"><span className={'bar-fill fill-'+s.toLowerCase()} style={{width:pct+'%'}}/></div></button>})}</div><div className="severity-footer"><ShieldCheck size={15}/><span>Severity is assigned by demo detection logic.</span></div></div>
        </section>
        <section className="panel alerts-panel"><div className="panel-heading alerts-heading"><div><h2>Priority alerts <span className="heading-count">{visibleAlerts.length}</span></h2><p>Review and investigate recent detections</p></div><button className="text-button" onClick={()=>setPage('Alerts')}>View all alerts <ChevronRight size={15}/></button></div><div className="table-tools"><div className="search-box"><Search size={16}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search alerts, IPs, techniques..." aria-label="Search alerts"/>{query&&<button onClick={()=>setQuery('')}><X size={13}/></button>}</div><div className="filter-tools"><Filter size={14}/><select value={severity} onChange={e=>setSeverity(e.target.value)} aria-label="Filter severity"><option>All</option><option>Critical</option><option>High</option><option>Medium</option><option>Low</option></select><select value={statusFilter} onChange={e=>setStatusFilter(e.target.value)} aria-label="Filter status"><option>All</option><option>New</option><option>Investigating</option><option>Contained</option><option>Closed</option><option>False Positive</option></select></div></div>
          <div className="table-scroll"><table><thead><tr><th>ALERT</th><th>SEVERITY</th><th>SOURCE / DESTINATION</th><th>DETECTION SOURCE</th><th>STATUS</th><th>TIME</th><th></th></tr></thead><tbody>{visibleAlerts.map(a=><tr key={a.id} onClick={()=>setSelected(a)} className="alert-row"><td><div className="alert-name"><span className={'alert-glyph '+(a.severity==='Critical'?'glyph-red':a.severity==='High'?'glyph-orange':'glyph-blue')}><ShieldAlert size={15}/></span><div><b>{a.title}</b><small>{a.id}</small></div></div></td><td><span className={severityClass(a.severity)}><span/> {a.severity}</span></td><td><div className="ip-cell"><span>{a.src_ip||'—'}</span><small>to {a.dst_ip||'—'}</small></div></td><td><span className="source-cell"><span className="source-icon">{a.source?.toLowerCase().includes('firewall')?<Network size={14}/>:a.source?.toLowerCase().includes('email')?<Bell size={14}/>:<Server size={14}/>}</span>{a.source}</span></td><td><span className={statusClass(a.status)}>{a.status}</span></td><td><span className="time-cell">{fmtTime(a.timestamp)}</span></td><td><button className="row-open" title="Investigate alert" onClick={e=>{e.stopPropagation();setSelected(a)}}><ChevronRight size={16}/></button></td></tr>)}</tbody></table>{visibleAlerts.length===0&&<div className="empty-state"><Search size={22}/><b>No matching alerts</b><span>Try changing your search or filters.</span><button className="text-button" onClick={()=>{setQuery('');setSeverity('All');setStatusFilter('All')}}>Clear filters</button></div>}</div><div className="table-footer"><span>Showing <b>{visibleAlerts.length}</b> of <b>{alerts.length}</b> alerts</span><span><span className="live-dot"/> {apiOnline?'Synced with local API':'Sample dataset'}</span></div>
        </section>
        <footer className="page-footer"><span> SENTINEL SOC <span className="footer-sep">·</span> PORTFOLIO LAB</span><span><LockKeyhole size={12}/> Authorized lab use only <span className="footer-sep">·</span> v0.1.0</span></footer>
      </div>
    </main>
    {selected&&<div className="drawer-backdrop" onClick={()=>setSelected(null)}><aside className="detail-drawer" onClick={e=>e.stopPropagation()}><div className="drawer-top"><div><span className="eyebrow">ALERT INVESTIGATION</span><h2>{selected.id}</h2></div><button className="icon-button" onClick={()=>setSelected(null)}><X size={18}/></button></div><div className="drawer-title"><span className={'alert-glyph '+(selected.severity==='Critical'?'glyph-red':selected.severity==='High'?'glyph-orange':'glyph-blue')}><ShieldAlert size={18}/></span><div><h3>{selected.title}</h3><p>{selected.description}</p></div></div><div className="drawer-badges"><span className={severityClass(selected.severity)}><span/>{selected.severity} severity</span><span className={statusClass(selected.status)}>{selected.status}</span></div><div className="detail-section"><h4>EVENT DETAILS</h4><div className="detail-grid"><Detail label="Source IP" value={selected.src_ip}/><Detail label="Destination IP" value={selected.dst_ip}/><Detail label="Detection source" value={selected.source}/><Detail label="Observed at" value={fmtTime(selected.timestamp)}/></div></div><div className="detail-section"><h4>MITRE ATT&CK MAPPING</h4><div className="mitre-card"><div className="mitre-icon"><Command size={17}/></div><div><b>{selected.technique||'Unmapped'} · {selected.technique_name||'Unmapped technique'}</b><p>Technique mapping is an analyst hypothesis; validate against the event evidence.</p></div><button className="small-icon" onClick={()=>setNotice('ATT&CK reference: attack.mitre.org/techniques/'+(selected.technique||'').replace('.','/')+'/')}><ArrowUpRight size={15}/></button></div></div><div className="detail-section"><h4>INVESTIGATION EVIDENCE</h4><ul className="evidence-list">{(selected.evidence||[]).map((e,i)=><li key={i}><CheckCircle2 size={15}/><span>{e}</span></li>)}</ul></div><div className="detail-section"><h4>CASE STATUS</h4><div className="status-actions">{['New','Investigating','Contained','Closed','False Positive'].map(s=><button key={s} className={'status-action '+(selected.status===s?'chosen':'')} onClick={()=>changeStatus(selected,s)}>{s}</button>)}</div></div><div className="drawer-note"><ShieldCheck size={16}/><span>Use evidence from authorized lab systems. Sample indicators use documentation IP ranges and are not live threat intelligence.</span></div></aside></div>}
    {notice&&<div className="toast"><CheckCircle2 size={16}/>{notice}<button onClick={()=>setNotice('')}><X size={14}/></button></div>}
  </div>;
}
function Metric({icon:Icon,label,value,note,accent,trend}) { return <div className="metric-card"><div className="metric-top"><span className={'metric-icon '+accent}><Icon size={18}/></span><span className="metric-trend">{trend}</span></div><div className="metric-value">{value}</div><div className="metric-label">{label}</div><div className="metric-note">{note}</div></div>; }
function Detail({label,value}) { return <div className="detail-item"><span>{label}</span><b>{value||'—'}</b></div>; }
createRoot(document.getElementById('root')).render(<React.StrictMode><App/></React.StrictMode>);

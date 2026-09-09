import { Link } from 'react-router-dom'
import { mockGraph } from '../types'

const nodeClass = (type) => type.toLowerCase().replaceAll(' ', '-')

export default function Graph() {
  return <div className="page-stack"><section className="page-intro"><span className="eyebrow">KNOWLEDGE GRAPH</span><h2>See why a migration is risky.</h2><p className="lede">Trace the path from an SQL operation to its affected object, risk, severity, and safer alternative.</p></section><section className="panel graph-panel"><div className="graph-toolbar"><span className="pill pill-soft">Preview: Customer table cleanup</span><Link className="text-link" to="/report">Open report →</Link></div><div className="graph-canvas">{mockGraph.nodes.map((node, index) => <div key={node.id} className={`graph-node ${nodeClass(node.node_type)}`} style={{ left: `${10 + (index % 3) * 31}%`, top: `${22 + Math.floor(index / 3) * 42}%` }}><small>{node.node_type}</small><strong>{node.label}</strong></div>)}<div className="graph-edge edge-a">AFFECTS</div><div className="graph-edge edge-b">MAY_CAUSE</div><div className="graph-edge edge-c">HAS_SEVERITY</div><div className="graph-edge edge-d">HAS_ALTERNATIVE</div></div><div className="graph-legend">{['Operation','Database Object','Risk','Severity','Safer Alternative'].map((type) => <span key={type}><i className={`legend-dot ${nodeClass(type)}`} />{type}</span>)}</div></section></div>
}

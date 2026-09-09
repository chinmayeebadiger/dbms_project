import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Background, Controls, MiniMap, ReactFlow } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { mockGraph } from '../types'
import { api } from '../services/api'

const nodeClass = (type) => type.toLowerCase().replaceAll(' ', '-')

const positions = [
  { x: 40, y: 150 }, { x: 280, y: 50 }, { x: 280, y: 245 },
  { x: 555, y: 115 }, { x: 820, y: 50 }, { x: 820, y: 245 },
]

function toReactFlowNodes(nodes) {
  return nodes.map((node, index) => ({
    id: node.id,
    position: positions[index % positions.length],
    data: { label: <><small>{node.node_type}</small><strong>{node.label}</strong></> },
    className: `graph-flow-node ${nodeClass(node.node_type)}`,
    style: { borderLeft: `4px solid ${node.node_type === 'Risk' ? '#d98d76' : node.node_type === 'Severity' ? '#dca85f' : node.node_type === 'Safer Alternative' ? '#6daa91' : '#76a7b6'}` },
  }))
}

function toReactFlowEdges(edges) {
  return edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: edge.relationship,
    animated: edge.relationship === 'MAY_CAUSE',
    style: { stroke: '#8daab4', strokeWidth: 1.5 },
    labelStyle: { fill: '#718890', fontSize: 9, fontWeight: 700 },
    labelBgStyle: { fill: '#fbfcfc', fillOpacity: 0.9 },
  }))
}

export default function Graph() {
  const [graph, setGraph] = useState(mockGraph)
  const [label, setLabel] = useState('Preview: Customer table cleanup')
  useEffect(() => {
    try {
      const saved = sessionStorage.getItem('latestAnalysis')
      const id = saved ? JSON.parse(saved).migration_id : null
      if (id) api.graph(id).then((data) => { setGraph(data); setLabel('Live analysis graph') }).catch(() => {})
    } catch {
      // Keep the preview graph when session storage is unavailable.
    }
  }, [])
  const nodes = useMemo(() => toReactFlowNodes(graph.nodes), [graph.nodes])
  const edges = useMemo(() => toReactFlowEdges(graph.edges), [graph.edges])
  return <div className="page-stack"><section className="page-intro"><span className="eyebrow">KNOWLEDGE GRAPH</span><h2>See why a migration is risky.</h2><p className="lede">Trace the path from an SQL operation to its affected object, risk, severity, and safer alternative.</p></section><section className="panel graph-panel"><div className="graph-toolbar"><span className="pill pill-soft">{label}</span><Link className="text-link" to="/report">Open report →</Link></div><div className="graph-flow-canvas"><ReactFlow nodes={nodes} edges={edges} fitView fitViewOptions={{ padding: 0.25 }} nodesDraggable nodesConnectable={false} attributionPosition="bottom-left"><Background color="#dfe9eb" gap={18} size={1} /><Controls showInteractive={false} /><MiniMap pannable zoomable nodeColor={(node) => node.className?.includes('risk') ? '#d98d76' : node.className?.includes('severity') ? '#dca85f' : '#76a7b6'} /></ReactFlow></div><div className="graph-legend">{['Operation','Database Object','Risk','Severity','Safer Alternative'].map((type) => <span key={type}><i className={`legend-dot ${nodeClass(type)}`} />{type}</span>)}</div></section></div>
}

<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>LinkNode Graph</title>
  <script src="https://unpkg.com/force-graph"></script>
  <style>
    html, body { height: 100%; margin: 0; background: #111; color: #fff; font-family: sans-serif; overflow: hidden; }
    #graph { width: 100%; height: 100%; }
  </style>
</head>
<body>
  <div id="graph"></div>
  <script>
    fetch('output/graph.json')
      .then(res => res.json())
      .then(data => {
        const Graph = ForceGraph()(document.getElementById('graph'))
          .graphData(data)
          .nodeId('id')
          .nodeAutoColorBy('group')
          .nodeLabel('id')
          .linkDirectionalArrowLength(4)
          .linkColor(() => 'rgba(255,255,255,0.25)')
          .nodeCanvasObject((node, ctx, globalScale) => {
            const label = node.id;
            const fontSize = 12/globalScale;
            ctx.font = `${fontSize}px Sans-Serif`;
            
            ctx.beginPath();
            ctx.arc(node.x, node.y, 4, 0, 2 * Math.PI, false);
            ctx.fillStyle = node.color || '#ff6b6b';
            ctx.fill();

            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.fillText(label, node.x + 6, node.y);
          })
          .nodePointerAreaPaint((node, color, ctx) => {
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI, false);
            ctx.fill();
          })
          // --- Add this block for click-to-zoom and actions ---
          .onNodeClick(node => {
            // Center camera on the node and zoom in smoothly
            Graph.centerAt(node.x, node.y, 1000); // 1000ms transition duration
            Graph.zoom(4, 1000);                  // Zoom level 4
            
            // Optional: Log data or trigger an external action
            console.log('Clicked node:', node);
          });
      });
  </script>
</body>
</html>
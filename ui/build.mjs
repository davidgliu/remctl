import { build } from 'esbuild';
import {readFile, readdir, writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const result = await build({entryPoints:['src/main.tsx'],bundle:true,write:false,minify:true,format:'iife',target:'es2022',loader:{'.png':'dataurl','.svg':'dataurl'},outdir:'dist'});
const script=result.outputFiles.find(f=>f.path.endsWith('.js')).text.replaceAll('</script','<\\/script');
const css=result.outputFiles.find(f=>f.path.endsWith('.css'))?.text || '';
const html = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>RemCTL</title><style>${css}</style></head><body><div id="root"></div><script>${script}</script></body></html>`;
await writeFile('../remctl_workspace.html', html);
// Both plugins run the installed CLI. Change their connection fingerprint for
// every shared module or generated interface so clients retire cached servers.
const fingerprint = createHash('sha256').update(html);
const modules = (await readdir('..')).filter(name => name === 'remctl' || /^remctl_.*\.py$/.test(name)).sort();
for (const name of [...modules, 'remctl_mcp_widget.html']) fingerprint.update(name + '\0').update(await readFile(`../${name}`));
const buildID = fingerprint.digest('hex').slice(0, 16);
for (const configPath of ['../plugins/remctl/mcp.json', '../plugins/claude-code/.mcp.json']) {
  const config = JSON.parse(await readFile(configPath, 'utf8'));
  config.mcpServers.remctl.env = {...config.mcpServers.remctl.env, REMCTL_PLUGIN_BUILD: buildID};
  await writeFile(configPath, JSON.stringify(config, null, 2) + '\n');
}

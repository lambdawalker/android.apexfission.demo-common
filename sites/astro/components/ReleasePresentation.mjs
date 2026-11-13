// Presentation only: immutable scope records remain untouched.
export const patchVersion = scope => scope.version.replace(/-(?:maven-central|jitpack)$/, '');
const provider = scope => /-(maven-central|jitpack)$/.exec(scope.version)?.[1];
export function equivalentPeers(scopes, scope, evidence = []) {
  const record = evidence.find(record => provider(scope) && record.module === scope.module && record.version === patchVersion(scope)
    && ['.aar', '-sources.jar', '-javadoc.jar'].every(key => /^[a-f0-9]{64}$/.test(record.sha256?.[key] || ''))
    && record.sources?.[provider(scope)] === scope.source);
  if (!record) return [scope];
  const peers = ['maven-central', 'jitpack'].map(name => scopes.find(peer => peer.module === scope.module
    && peer.language === scope.language && peer.version === `${record.version}-${name}` && peer.source === record.sources[name]));
  return peers.every(Boolean) ? peers : [scope];
}
export function versionOptions(ordered, current, guide, destination, evidence = []) {
  const seen = new Set();
  return ordered.flatMap(scope => {
    const peers = equivalentPeers(ordered, scope, evidence);
    const target = peers.find(peer => provider(peer) === 'maven-central') || scope;
    if (seen.has(target.root)) return [];
    seen.add(target.root);
    const patch = patchVersion(scope);
    const ambiguous = peers.length === 1 && ordered.some(peer => peer !== scope && patchVersion(peer) === patch);
    return [{label: scope.development ? 'Development' : ambiguous ? scope.version : patch,
      href: destination(target, guide), selected: peers.some(peer => peer.version === current.version)}];
  });
}
export function publications(scopes, scope, evidence = []) {
  if (scope.development) return [];
  return equivalentPeers(scopes, scope, evidence).flatMap(peer => {
    const names = peer.destinations || (provider(peer) ? [provider(peer)] : []);
    return names.map(name => ({name, source: peer.source, href: `${peer.root}installation/`}));
  });
}

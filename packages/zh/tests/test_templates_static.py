from pathlib import Path
import ast
import json
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def test_required_files_exist():
    for rel in [
        'SKILL.md', 'README.md', 'CHANGELOG.md',
        'templates/manifest.yml', 'templates/AGENTS.md',
        'templates/ai-dev/DOC_UPDATE_TRIGGERS.yml',
        'templates/ai-dev/orchestration/AGENT_ROLE_POLICY.md',
        'templates/ai-dev/orchestration/CONTEXT_COMPACTION_POLICY.md',
        'templates/scripts/ai_doc_impact_check.py',
        'templates/scripts/architecture_check.py',
        'templates/scripts/thread_coordination_check.py',
        'templates/scripts/project_auto_commit.py',
        'templates/codex-config/hooks.json',
        'templates/codex-config/config.toml',
        'templates/ai-dev/git/AUTO_COMMIT_POLICY.md',
        'templates/ai-dev/git/AUTO_COMMIT_CONFIG.json',
        'templates/codex-agents/main-session-coordinator.toml',
        'bin/apply_ai_doc_driven_project.py',
        'bin/apply_skill.py',
        'bin/validate_skill_package.py',
        'bin/build_release.py',
        'schemas/manifest.schema.json',
        'templates/schemas/manifest.schema.json',
    ]:
        assert (ROOT / rel).exists(), rel


def test_python_scripts_parse():
    for rel in [
        'templates/scripts/ai_doc_impact_check.py',
        'templates/scripts/architecture_check.py',
        'templates/scripts/thread_coordination_check.py',
        'templates/scripts/project_auto_commit.py',
        'bin/apply_ai_doc_driven_project.py',
        'bin/apply_skill.py',
        'bin/validate_skill_package.py',
        'bin/build_release.py',
    ]:
        ast.parse((ROOT / rel).read_text(encoding='utf-8'))


def test_manifest_json_compatible():
    data = json.loads((ROOT / 'templates/manifest.yml').read_text(encoding='utf-8'))
    assert data['skill_name'] == 'ai-doc-driven-project'
    assert data['skill_version'] == '0.3.4'
    assert data['skill_revision_time'] == '2026-06-06T04:45:00+08:00'
    assert data['root_files'][0]['target'] == 'AGENTS.md'
    assert any(item['source'] == 'templates/codex-config' for item in data['copy_trees'])
    assert '*.local.md' not in data['gitignore_entries']
    assert '.ai-secrets/*.local.md' in data['gitignore_entries']
    assert 'generated_safe_replace' in data['update_policy']


def test_doc_update_triggers_json_compatible_and_new_triggers():
    data = json.loads((ROOT / 'templates/ai-dev/DOC_UPDATE_TRIGGERS.yml').read_text(encoding='utf-8'))
    assert data['version'] == '0.3.4'
    for key in ['skill_revision_metadata', 'codex_context_compaction', 'agent_role_policy', 'thread_coordination_enforcement', 'release_package_validation', 'project_auto_commit_policy']:
        assert key in data['triggers']


def test_agents_template_has_metadata_stamp_placeholder():
    text = (ROOT / 'templates/AGENTS.md').read_text(encoding='utf-8')
    assert text.startswith('<!-- ai-skill: ai-doc-driven-project')
    assert 'revision-time: 2026-06-06T04:45:00+08:00' in text
    assert 'REPLACE_WITH_APPLY_TIME' not in text
    assert 'skill-version: 0.3.4' in text


def test_codex_agents_have_required_fields():
    agents = sorted((ROOT / 'templates/codex-agents').glob('*.toml'))
    assert agents
    names = set()
    for path in agents:
        data = tomllib.loads(path.read_text(encoding='utf-8'))
        for field in ['name', 'description', 'developer_instructions']:
            assert isinstance(data.get(field), str) and data[field].strip(), f'{path}: {field}'
        names.add(data['name'])
    assert 'main-session-coordinator' in names
    assert 'thread-manager' in names
    assert 'merge-coordinator' in names


def test_hooks_json_parse_and_non_mutating_defaults():
    data = json.loads((ROOT / 'templates/codex-config/hooks.json').read_text(encoding='utf-8'))
    assert 'hooks' in data
    for event in ['SessionStart', 'PreCompact', 'PostCompact', 'SubagentStop', 'Stop']:
        assert event in data['hooks']
    text = (ROOT / 'templates/codex-config/hooks.json').read_text(encoding='utf-8')
    assert '--hook-json' in text
    assert '--event Stop --record' not in text
    assert '--event SubagentStop --record' not in text


def test_codex_config_parse():
    data = tomllib.loads((ROOT / 'templates/codex-config/config.toml').read_text(encoding='utf-8'))
    assert data['agents']['max_threads'] == 4
    assert data['agents']['max_depth'] == 1


def test_no_runtime_run_records_in_templates():
    for p in ROOT.rglob('*'):
        rel = p.relative_to(ROOT).as_posix()
        assert '.ai-secrets' not in rel.split('/'), p
        assert not re.search(r'(TC|DUR)-\d{8}-\d{6}\.md$', p.name), p


def test_package_validator_checks_generated_artifacts():
    text = (ROOT / 'bin/validate_skill_package.py').read_text(encoding='utf-8')
    assert '.pytest_cache' in text
    assert '__pycache__' in text
    assert 'TC-' in text and 'DUR-' in text


def test_no_legacy_gitkeep_files():
    assert not list(ROOT.glob('templates/**/gitkeep'))


def test_no_secret_template_name():
    assert not (ROOT / 'templates/env/test-secrets.template.md').exists()
    assert (ROOT / 'templates/env/TEST_SECRETS_FORMAT.md').exists()


def test_secret_scanner_does_not_skip_real_key_after_redacted_example(tmp_path):
    import importlib.util
    script = ROOT / 'templates/scripts/ai_doc_impact_check.py'
    spec = importlib.util.spec_from_file_location('impact_check', script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    sample = tmp_path / 'notes.txt'
    
    key_name = 'API_' + 'KEY'
    fake_value = 'ABCDEFGHIJKLMNOPQRSTUVWX'
    sample.write_text('Example: <redacted>\n' + key_name + '=' + fake_value + '\n', encoding='utf-8')
    issues = module.file_secret_issues(sample)
    assert issues


def test_update_mode_writes_migration_report_by_default():
    text = (ROOT / 'bin/apply_ai_doc_driven_project.py').read_text(encoding='utf-8')
    assert 'no_migration_report' in text
    assert 'args.mode == \"update\" and args.write and not args.no_migration_report' in text


def test_auto_commit_policy_defaults_disabled():
    cfg = json.loads((ROOT / 'templates/ai-dev/git/AUTO_COMMIT_CONFIG.json').read_text(encoding='utf-8'))
    assert cfg['enabled'] is False
    assert cfg['allow_auto_stage'] is False
    assert cfg['allow_auto_commit'] is False
    assert cfg['allow_auto_push'] is False
    assert '.ai-secrets/**' in cfg['protected_paths']
    text = (ROOT / 'templates/ai-dev/git/AUTO_COMMIT_POLICY.md').read_text(encoding='utf-8')
    assert 'project_auto_commit.py' in text
    assert 'push' in text.lower()


def test_project_auto_commit_script_mentions_no_push():
    text = (ROOT / 'templates/scripts/project_auto_commit.py').read_text(encoding='utf-8')
    assert 'never pushes' in text.lower() or 'never push' in text.lower()
    assert 'allow_auto_commit' in text
    assert 'allow_auto_push' in text



def test_repository_governance_files_exist():
    for rel in ['LICENSE', 'NOTICE', 'SECURITY.md', 'TEMPLATE_OUTPUT_LICENSE.md']:
        assert (ROOT / rel).exists(), rel

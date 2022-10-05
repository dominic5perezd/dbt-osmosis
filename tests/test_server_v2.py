from pathlib import Path

from fastapi.testclient import TestClient

from dbt_osmosis.core.server_v2 import app

from tests.sqlfluff_templater.fixtures.dbt.templater import profiles_dir, project_dir, sqlfluff_config_path  # noqa: F401

client = TestClient(app)


def test_lint(profiles_dir, project_dir, sqlfluff_config_path):
    response = client.post(
            "/register",
            params={
                "project_dir": project_dir,
                "profiles_dir": profiles_dir,
                "config_path": sqlfluff_config_path,
                "target": "dev",
            },
            headers={"X-dbt-Project": "dbt_project"},
        )
    assert response.status_code == 200
    assert response.json() == {'added': 'dbt_project', 'projects': ['dbt_project']}
    sql_path = Path(project_dir) / "models" / "my_new_project" / "issue_1608.sql"
    response = client.post(
        "/lint",
        headers={"X-dbt-Project": "dbt_project"},
        params={
            #"query": sql_path.read_text(),
            #"query": "SELECT DISTINCT(a) FROM b",
            "query": "SELEC",
            "config_path": sqlfluff_config_path,
        }
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {'result': [{'code': 'L003',
             'description': 'Expected 2 indentations, found less than 2 '
                            '[compared to line 03]',
             'line_no': 4,
             'line_pos': 6},
            {'code': 'L023',
             'description': "Single whitespace expected after 'AS' in 'WITH' "
                            'clause.',
             'line_no': 7,
             'line_pos': 7}]}



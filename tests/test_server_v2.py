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
            "query": sql_path.read_text(),
            "config_path": sqlfluff_config_path,
        }
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json["result"]) == 1
    del response_json["result"][0]["description"]
    assert response_json == {'result': [{'code': 'TMP',
             # 'description': 'Unrecoverable failure in Jinja templating: '
             #                '<sqlfluff.core.templaters.jinja.JinjaTemplater.process.<locals>.UndefinedRecorder '
             #                'object at 0x10d084400> is not safely callable. '
             #                'Have you configured your variables? '
             #                'https://docs.sqlfluff.com/en/latest/configuration.html',
             'line_no': 1,
             'line_pos': 1}]}


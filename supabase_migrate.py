# -*- coding: utf-8 -*-
"""
Supabase DB 마이그레이션 실행
.env의 DATABASE_URL로 연결 후 supabase/migrations/001_initial_tables.sql 적용
실행: python supabase_migrate.py
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import psycopg2

load_dotenv()

ROOT = Path(__file__).resolve().parent
MIGRATION_FILE = ROOT / "supabase" / "migrations" / "001_initial_tables.sql"


def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        user = os.getenv("user", "postgres")
        password = os.getenv("password")
        host = os.getenv("host")
        port = os.getenv("port", "5432")
        dbname = os.getenv("dbname", "postgres")
        if not all([password, host]):
            print("오류: .env에 DATABASE_URL 또는 (user, password, host, port, dbname)을 설정하세요.")
            sys.exit(1)
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

    if not MIGRATION_FILE.exists():
        print(f"오류: 마이그레이션 파일을 찾을 수 없습니다. {MIGRATION_FILE}")
        sys.exit(1)

    sql = MIGRATION_FILE.read_text(encoding="utf-8")

    # 정책이 이미 있으면 오류가 나므로, 정책만 DROP 후 재생성 (선택)
    # 여기서는 전체 SQL을 한 번 실행. 최초 1회 실행 가정.
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql)
        cur.close()
        conn.close()
        print("마이그레이션 적용 완료: sites, personnel, certificates 테이블 및 RLS 정책 생성됨.")
    except psycopg2.Error as e:
        if "already exists" in str(e):
            print("테이블 또는 정책이 이미 존재합니다. 스키마는 적용된 상태일 수 있습니다.")
            print("상세:", e)
        else:
            print("마이그레이션 실패:", e)
            sys.exit(1)


if __name__ == "__main__":
    main()

# Supabase 클라이언트 사용법 (JavaScript/프론트엔드)

## 올바른 초기화

**잘못된 예** (환경 변수 이름이 아니라 키 문자열을 붙인 경우):
```js
const supabaseKey = process.env.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
// ❌ process.env. 뒤에는 "변수 이름"이 와야 합니다.
```

**올바른 예**:
```js
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://hhpofxpnztzibtpkpiar.supabase.co'
const supabaseKey = process.env.SUPABASE_ANON_KEY   // .env에 SUPABASE_ANON_KEY=eyJhbG... 설정
const supabase = createClient(supabaseUrl, supabaseKey)
```

- `.env` 파일에 **변수 이름** `SUPABASE_ANON_KEY` 를 두고, **값**으로 anon 키 문자열을 넣습니다.
- 코드에서는 `process.env.SUPABASE_ANON_KEY` 로 읽습니다.

## 프로젝트에서 사용

### 1) 공용 클라이언트 사용 (권장)

이미 만들어 둔 파일을 import 하세요:

```js
import { supabase } from './js/supabaseClient.js'
// 사용 예
const { data, error } = await supabase.from('sites').select('*')
```

- `js/supabaseClient.js` 가 `SUPABASE_URL` / `SUPABASE_ANON_KEY` (또는 Vite면 `VITE_SUPABASE_*`) 를 읽어서 `createClient` 합니다.

### 2) Vite 사용 시

- `.env` 에 다음처럼 설정:
  ```
  VITE_SUPABASE_URL=https://hhpofxpnztzibtpkpiar.supabase.co
  VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
- 코드에서는 `import.meta.env.VITE_SUPABASE_URL`, `import.meta.env.VITE_SUPABASE_ANON_KEY` 사용 (또는 `js/supabaseClient.js` 사용).

### 3) anon 키 보안

- **anon** 키는 브라우저에 노출되어도 됩니다. 보안은 Supabase **RLS(Row Level Security)** 정책으로 처리합니다.
- **service_role** 키는 서버에서만 사용하고, 브라우저/클라이언트에는 두지 마세요.

## .env 예시

```env
SUPABASE_URL=https://hhpofxpnztzibtpkpiar.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhocG9meHBuenR6aWJ0cGtwaWFyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc2MDc2NjgsImV4cCI6MjA4MzE4MzY2OH0.qYgw_6KlgPZrQPvLs0IJKb-HRZaWMJxiKv0H4izysAs
```

이렇게 설정한 뒤 `process.env.SUPABASE_ANON_KEY` 로 사용하면 됩니다.

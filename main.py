import json

EPSILON = 1e-9  # 판정 시 "사실상 같다"고 볼 오차 허용 범위. Day 3 data.json에도 동일하게 적용됨

# 원본 데이터에 섞여 있는 여러 표기(왼쪽)를 우리 프로그램의 표준 라벨(오른쪽)로 통일하는 대응표
# 'Cross', 'X' 자체도 넣어둔 건 이미 표준형으로 들어온 값도 그대로 통과시키기 위함
LABEL_MAP = {
    '+': 'Cross',
    'cross': 'Cross',
    'Cross': 'Cross',
    'x': 'X',
    'X': 'X',
}

def normalize_label(raw):
    # raw(원본 표기 문자열)가 표에 있으면 표준 라벨로 바꿔서 반환
    if raw in LABEL_MAP:
        return LABEL_MAP[raw]
    # 표에 없는 값(오타, 알 수 없는 라벨 등)이면 "값 없음"을 뜻하는 None 반환
    # → 호출하는 쪽에서 None을 보고 이 케이스를 FAIL 처리하게 됨
    return None

def mac(pattern, filter_grid):
    total = 0
    size = len(pattern)
    for i in range(size):
        for j in range(size):
            total = total + pattern[i][j] * filter_grid[i][j]
    return total

def read_grid(title, size):
    print(title)  # 사용자에게 무엇을 입력해야 하는지 안내 문구 출력

    grid = []  # 검증을 통과한 줄들을 담을 빈 리스트 (최종적으로 2차원 리스트가 됨)

    while len(grid) < size:  # grid에 size개(예: 3개)의 줄이 모일 때까지 반복
        line = input()          # 사용자가 엔터를 칠 때까지 대기, 입력한 문자열 전체를 받음 (예: "0 1 0")
        parts = line.split()    # 공백 기준으로 잘라 문자열 리스트로 변환 (예: ['0', '1', '0'])

        if len(parts) != size:  # 입력한 숫자 개수가 size와 다르면
            print('입력 형식 오류: 각 줄에 %d개의 숫자를 공백으로 구분해 입력하세요.' % size)
            continue             # 이번 줄은 버리고 while 맨 위로 돌아가 다시 입력받음 (grid는 그대로라 재시도됨)

        try:
            row = [float(p) for p in parts]  # 문자열 리스트를 실수 리스트로 변환 시도 (예: ['0','1','0'] -> [0.0, 1.0, 0.0])
        except ValueError:                    # 변환 중 숫자가 아닌 글자를 만나면 여기로 옴 (예: 'a')
            print('입력 형식 오류: 숫자만 입력하세요.')
            continue                           # 이번 줄도 버리고 다시 입력받음

        grid.append(row)  # 개수 검사와 변환을 모두 통과한 줄만 grid에 추가 (이때만 while 조건에 가까워짐)

    return grid  # size개의 줄이 다 모이면 완성된 2차원 리스트를 반환

def print_grid(grid):
    for row in grid:                              # grid의 각 줄(row, 1차원 리스트)을 하나씩 꺼냄
        print(' '.join(str(v) for v in row))       # row 안의 각 값(v)을 문자열로 바꾼 뒤 공백으로 이어붙여 한 줄로 출력
        # 예: row = [0.0, 1.0, 0.0] -> str(v)들: '0.0','1.0','0.0' -> join 결과: "0.0 1.0 0.0"

def check_grid(grid, size):
    # 패턴이 실제로 size x size 모양인지 검증. 문제 있으면 "이유 문자열"을, 없으면 None을 반환
    # (True/False가 아니라 이유를 돌려주는 이유: 실패 사유를 화면/README에 남겨야 하는 미션 요구사항 때문)

    if not isinstance(grid, list):
        # grid 자체가 리스트가 아닌 경우 (남이 만든 파일이라 숫자나 문자열이 들어있을 수도 있음)
        return '2차원 배열이 아님'

    if len(grid) != size:
        # 행(바깥 리스트 원소) 개수가 기대한 size와 다른 경우
        return '행 수가 %d이 아님 (실제 %d)' % (size, len(grid))

    for row in grid:
        # 모든 행을 돌면서, 각 행이 리스트인지 + 길이가 size와 같은지 확인
        if not isinstance(row, list) or len(row) != size:
            return '열 수가 %d이 아닌 행이 있음' % size

    # 여기까지 왔다는 건 모든 검사를 통과했다는 뜻
    return None

def judge(score_a, score_b, label_a, label_b):
    # label_a, label_b를 인자로 받는 이유: 모드1에서는 'A'/'B', Day3 모드2에서는 'Cross'/'X'를
    # 넘기면 이 함수 하나를 그대로 재사용할 수 있기 때문
    if abs(score_a - score_b) < EPSILON:
        # 동점 검사를 가장 먼저 함 — 크기 비교(>)를 먼저 하면
        # 반올림 오차만으로 승자가 정해져버려서 동점 검사가 무의미해짐
        return 'UNDECIDED'
    if score_a > score_b:
        return label_a
    return label_b  # score_a <= score_b인 경우 (동점은 이미 위에서 걸러졌으므로 실질적으로 score_b가 더 큰 경우)

def mode_user_input():
    print()
    print('#---------------------------------------')
    print('# [1] 필터 입력')
    print('#---------------------------------------')

    # 필터 A, B를 각각 3x3으로 입력받음 (read_grid가 개수/형식 검증까지 알아서 처리)
    filter_a = read_grid('필터 A (3줄 입력, 공백 구분)', 3)
    print('필터 A 저장 완료')
    print_grid(filter_a)   # 입력이 제대로 저장됐는지 사람이 눈으로 확인 (미션 요구사항의 "저장 확인")
    print()

    filter_b = read_grid('필터 B (3줄 입력, 공백 구분)', 3)
    print('필터 B 저장 완료')
    print_grid(filter_b)

    print()
    print('#---------------------------------------')
    print('# [2] 패턴 입력')
    print('#---------------------------------------')
    pattern = read_grid('패턴 (3줄 입력, 공백 구분)', 3)
    print('패턴 저장 완료')
    print_grid(pattern)

    # 어제 만든 mac()을 그대로 재사용 — 패턴 vs 필터A, 패턴 vs 필터B 각각 점수 계산
    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)

    # judge()에 'A', 'B'를 라벨로 넘김 (Day3에서는 여기 자리에 'Cross', 'X'가 들어갈 예정)
    verdict = judge(score_a, score_b, 'A', 'B')

    print()
    print('#---------------------------------------')
    print('# [3] MAC 결과')
    print('#---------------------------------------')
    print('A 점수:', score_a)
    print('B 점수:', score_b)

    if verdict == 'UNDECIDED':
        print('판정: 판정 불가 (|A-B| < %g)' % EPSILON)
    else:
        print('판정: %s' % verdict)

def load_filters(data):
    print('#---------------------------------------')
    print('# [1] 필터 로드')
    print('#---------------------------------------')

    filters = {}  # 최종적으로 {'size_5': {'Cross': ..., 'X': ...}, 'size_13': {...}, ...} 형태가 됨

    # data.get('filters', {}) — data['filters']와 비슷하지만, 'filters' 키가 없어도
    # 에러 대신 빈 딕셔너리를 반환 (파일이 이상해도 프로그램이 죽지 않게 하는 안전장치)
    raw_filters = data.get('filters', {})

    # sorted(...)에 key=lambda를 안 주면 문자열 순서로 정렬돼서 'size_13'이 'size_5'보다 먼저 옴
    # key=lambda k: int(k.split('_')[1])  →  'size_13'을 ['size','13']으로 쪼개 '13'을 꺼낸 뒤
    #                                         정수로 바꿔서 그 숫자 기준으로 정렬 (5, 13, 25 순서가 됨)
    for key in sorted(raw_filters, key=lambda k: int(k.split('_')[1])):
        bucket = {}  # 이 크기(key)에 해당하는 {'Cross': grid, 'X': grid}를 담을 그릇

        # .items() — 딕셔너리에서 (키, 값) 쌍을 하나씩 꺼냄. 여기선 (원본이름, 격자데이터) 쌍
        for raw_name, grid in raw_filters[key].items():
            label = normalize_label(raw_name)  # 'cross' -> 'Cross' 등으로 표준화

            if label is None:
                # 정규화 표에 없는 이상한 이름이면 경고만 찍고 이 항목은 건너뜀
                print('  경고: 알 수 없는 필터 이름 %s (무시)' % raw_name)
                continue

            bucket[label] = grid  # ★ 정규화의 실체: 원본 표기가 뭐였든 표준 라벨로 저장

        filters[key] = bucket
        # %-8s : 문자열을 왼쪽 정렬해서 최소 8칸으로 맞춤 (출력 줄맞춤용)
        # ', '.join(sorted(bucket)) : bucket의 키들(예: ['Cross','X'])을 정렬 후 콤마로 이어붙여 출력
        print('OK %-8s 필터 로드 완료 (%s)' % (key, ', '.join(sorted(bucket))))

    return filters

def analyze_patterns(data, filters):
    print()
    print('#---------------------------------------')
    print('# [2] 패턴 분석 (라벨 정규화 적용)')
    print('#---------------------------------------')

    results = []  # (케이스이름, 통과여부 True/False, 실패사유) 튜플들을 모아둘 리스트

    for case_id, item in data.get('patterns', {}).items():
        print('--- %s ---' % case_id)

        # [관문 1] 케이스 이름('size_5_1')에서 숫자(크기) 뽑기
        try:
            size = int(case_id.split('_')[1])  # 'size_5_1' -> ['size','5','1'] -> '5' -> 5
        except (IndexError, ValueError):
            # split 결과에 [1]번이 없으면 IndexError, int() 변환 실패하면 ValueError
            # 지금 data.json엔 이런 케이스가 없지만, 남이 준 파일은 언제 바뀔지 모르니 대비
            print('FAIL: 케이스 이름에서 크기를 읽을 수 없음')
            results.append((case_id, False, '케이스 이름 형식 오류'))
            continue  # 이 케이스는 포기하고 다음 case_id로

        # [관문 2] 그 크기의 필터가 로드되어 있나
        filter_key = 'size_%d' % size
        if filter_key not in filters:
            print('FAIL: %s 필터가 없음' % filter_key)
            results.append((case_id, False, '%s 필터 없음' % filter_key))
            continue

        bucket = filters[filter_key]  # {'Cross': grid, 'X': grid}

        # [관문 3] 패턴이 실제로 size x size 모양인가
        pattern = item.get('input')
        problem = check_grid(pattern, size)
        if problem:  # None이 아니면(=문제 있으면) 여기로
            print('FAIL: 패턴 크기 오류 - %s' % problem)
            results.append((case_id, False, '패턴 크기 오류'))
            continue

        # [관문 4] expected 값('x', '+' 등)을 표준 라벨로 바꿀 수 있나
        expected = normalize_label(item.get('expected'))
        if expected is None:
            # %r : repr() 형태로 출력 (문자열이면 따옴표까지 보여줘서 원본 값을 정확히 확인 가능)
            print('FAIL: expected 값을 표준 라벨로 바꿀 수 없음 (%r)' % item.get('expected'))
            results.append((case_id, False, 'expected 라벨 오류'))
            continue

        # --- 여기까지 왔으면 4개 관문을 다 통과 → 실제 채점 ---
        score_cross = mac(pattern, bucket['Cross'])
        score_x = mac(pattern, bucket['X'])
        verdict = judge(score_cross, score_x, 'Cross', 'X')  # 어제 만든 judge()를 라벨만 바꿔 재사용

        print('Cross 점수:', score_cross)
        print('X 점수:', score_x)

        if verdict == expected:
            print('판정: %s | expected: %s | PASS' % (verdict, expected))
            results.append((case_id, True, ''))
        elif verdict == 'UNDECIDED':
            # 동점이라 판정 불가로 답한 케이스 — 정답과 다르니 FAIL이지만, 근거 없이 찍은 게 아니라
            # "판별 불가능한 문제였다"는 게 이유. data.json에 의도적으로 심어둔 3개가 여기 해당
            print('판정: UNDECIDED | expected: %s | FAIL (동점 규칙)' % expected)
            results.append((case_id, False, '동점(UNDECIDED) 처리 규칙에 따라 FAIL'))
        else:
            print('판정: %s | expected: %s | FAIL' % (verdict, expected))
            results.append((case_id, False, '판정 불일치'))

    return results

def mode_json():
    print()

    # 파일 열기를 try로 감싸서, 파일이 없거나 형식이 깨져도 프로그램이 죽지 않게 함
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            # with ... as f:  → 이 블록이 끝나면 파일을 자동으로 닫아줌 (닫는 걸 깜빡할 일이 없음)
            # encoding='utf-8' → 한글/특수문자가 깨지지 않게 명시
            data = json.load(f)  # 파일 내용을 읽어서 파이썬 딕셔너리로 변환
    except FileNotFoundError:
        # data.json이 main.py와 같은 폴더에 없을 때 발생
        print('오류: data.json 파일을 찾을 수 없습니다. main.py와 같은 폴더에 두세요.')
        return  # 여기서 함수를 끝냄 (아래 코드는 실행 안 됨)
    except json.JSONDecodeError as e:
        # JSON 문법이 깨져 있을 때 발생 (쉼표 누락 등). e에 구체적인 오류 정보가 담김
        print('오류: data.json 형식이 잘못되었습니다 - %s' % e)
        return

    # --- 여기까지 왔다는 건 data.json을 성공적으로 읽었다는 뜻 ---
    filters = load_filters(data)               # ★ 스텝5에서 만든 함수, 여기서 처음 호출됨
    results = analyze_patterns(data, filters)   # ★ 스텝6에서 만든 함수, 여기서 호출됨
    summary_section(results)                    # ★ 방금 만든 함수, 여기서 호출됨

def summary_section(results):
    total = len(results)  # 전체 케이스 개수 (튜플 리스트의 길이)

    # sum(1 for r in results if r[1])
    #   → results를 훑으면서, 각 튜플 r의 두 번째 원소(r[1] = 통과여부 True/False)가
    #     True인 것마다 1을 세서 더함. 즉 "통과 개수 세기"를 한 줄로 압축한 것
    #   → 리스트 컴프리헨션과 비슷한 문법(제너레이터 표현식)이 sum() 안에 바로 들어간 형태
    passed = sum(1 for r in results if r[1])
    failed = total - passed

    print()
    print('#---------------------------------------')
    print('# [4] 결과 요약')
    print('#---------------------------------------')
    print('총 테스트: %d개' % total)
    print('통과: %d개' % passed)
    print('실패: %d개' % failed)

    if failed:  # failed가 0이면 False 취급, 1 이상이면 True 취급 (파이썬은 0을 False처럼 씀)
        print()
        print('실패 케이스:')
        # results의 각 튜플 (case_id, ok, reason)을 세 변수로 언패킹
        for case_id, ok, reason in results:
            if not ok:  # ok가 False인 것만(=실패한 것만) 출력
                print('- %s: %s' % (case_id, reason))

def main():
    print('=== Mini NPU Simulator ===')
    print()
    print('[모드 선택]')
    print('1. 사용자 입력 (3x3)')
    print('2. data.json 분석')

    while True:  # 유효한 선택(1 또는 2)이 나올 때까지 계속 물어봄
        choice = input('선택: ').strip()  # strip()으로 앞뒤 공백 제거 (실수로 스페이스 눌러도 통과)

        if choice == '1':
            mode_user_input()
            return       # main() 종료 → 프로그램 종료
        if choice == '2':
            mode_json()   # ← '(내일 만듭니다)' 대신 이걸로 교체
            return
        print('1 또는 2를 입력하세요.')  # 잘못된 입력이면 안내 후 while 처음으로 돌아가 재질문


main()  # 이 줄이 있어야 파일을 실행했을 때 실제로 프로그램이 시작됨

cross_filter = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
]

x_filter = [
    [1, 0, 1],
    [0, 1, 0],
    [1, 0, 1]
]

cross_pattern = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
]

x_pattern = [
    [1, 0, 1],
    [0, 1, 0],
    [1, 0, 1]
]

print("십자가 패턴 vs 십자가 필터:", mac(cross_pattern, cross_filter))
print("십자가 패턴 vs X 필터:", mac(cross_pattern, x_filter))
print("X 패턴 vs 십자가 필터:", mac(x_pattern, cross_filter))
print("X 패턴 vs X 필터:", mac(x_pattern, x_filter))


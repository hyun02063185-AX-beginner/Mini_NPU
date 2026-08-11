import json
import time

EPSILON = 1e-9  # 판정 시 "사실상 같다"고 볼 오차 허용 범위. Day 3 data.json에도 동일하게 적용됨
REPEAT = 10  # 성능 측정 시 반복 횟수. 나중에 100/1000으로 바꿔 실험할 때 이 한 곳만 고치면 됨
BONUS_REPEAT = 1000
# 오늘 비교하는 건 "같은 크기"에서 2D vs 1D의 차이인데, 그 차이가 크기별 차이보다 훨씬 작음.
# 10회로 재면 측정 잡음이 실제 차이보다 커서 개선율 부호가 뒤집히는 현상이 생기므로 1000회로 늘림.
# 기본 과제 성능표(REPEAT=10)는 그대로 두고, 비교 전용으로만 이 상수를 씀


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

def flatten(grid):
    # 2차원 격자를 1차원 리스트로 폄: [[1,2],[3,4]] -> [1,2,3,4]
    # 행을 위에서부터 순서대로 이어붙이므로 결과 길이는 항상 N*N
    flat = []
    for row in grid:
        for value in row:
            flat.append(value)
    return flat

def mac_flat(flat_a, flat_b):
    # mac()과 결과값은 완전히 같아야 함. 다른 건 인덱싱과 반복문 구조뿐
    # (두 리스트 길이가 같다고 전제 — flatten() 결과끼리만 넘길 것이므로)
    total = 0.0
    for k in range(len(flat_a)):
        total = total + flat_a[k] * flat_b[k]
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

def measure(pattern, filter_grid):
    start = time.perf_counter()  # 반복 시작 직전 시각

    for _ in range(REPEAT):
        # '_'는 "이 변수를 실제로 안 쓴다"는 관례적 이름. range(10)이 주는 0~9 값을 받을 변수가
        # 필요하긴 한데(for문 문법상), 값 자체는 안 쓰고 "10번 돌린다"는 게 목적이라 _로 표시
        mac(pattern, filter_grid)
        # 반환값(total)을 안 받고 그냥 호출만 함 — 여기선 "계산이 실제로 실행되는 시간"만 재는 게
        # 목적이라 결과값은 필요 없음. print나 파일 읽기가 이 안에 없는 것도 같은 이유
        # (미션이 "I/O 제외, 연산 함수 호출 구간만" 측정하라고 요구했기 때문)

    end = time.perf_counter()  # 10번 다 돈 직후 시각

    return (end - start) / REPEAT * 1000
    # (end - start) : 10번 도는 데 걸린 총 시간(초)
    # / REPEAT       : 10으로 나눠서 1회당 평균 시간(초)
    # * 1000         : 초 -> 밀리초(ms) 단위로 변환

def measure_flat(flat_a, flat_b):
    # mac_flat() 1회 평균 시간(ms). measure()와 구조는 완전히 동일, 대상만 mac_flat으로 바뀜
    start = time.perf_counter()
    for _ in range(BONUS_REPEAT):
        mac_flat(flat_a, flat_b)
    end = time.perf_counter()
    return (end - start) / BONUS_REPEAT * 1000

def measure_bonus(pattern, filter_grid):
    # mac() 1회 평균 시간(ms). 기존 measure()는 REPEAT(10)를 쓰므로 건드리지 않고,
    # "2D를 BONUS_REPEAT(1000)로 잰 버전"을 별도로 만듦 — 1D와 동일 조건으로 비교하기 위함
    start = time.perf_counter()
    for _ in range(BONUS_REPEAT):
        mac(pattern, filter_grid)
    end = time.perf_counter()
    return (end - start) / BONUS_REPEAT * 1000

def print_perf_table(items):
    # items는 (크기, 패턴, 필터) 튜플들의 리스트가 들어올 예정 (스텝6에서 채워짐)

    print('크기       평균 시간(ms)     연산 횟수')
    print('-' * 38)  # '-'를 38번 반복해서 구분선 생성 (문자열 * 정수 = 반복, 어제 '2'*3 실험과 같은 원리)

    for size, pattern, filter_grid in items:  # 튜플 3개를 한 번에 세 변수로 언패킹
        avg_ms = measure(pattern, filter_grid)  # 방금 만든 measure()로 평균 시간 계산
        label = '%dx%d' % (size, size)          # 예: size=5 -> '5x5'

        # %-10s : 문자열을 왼쪽 정렬, 최소 10칸
        # %12.4f : 실수를 12칸 너비로, 소수점 아래 4자리까지
        # %10d  : 정수를 10칸 너비로 (오른쪽 정렬이 기본이라 자릿수가 눈에 잘 들어옴)
        print('%-10s %12.4f %10d' % (label, avg_ms, size * size))
        # size * size = 연산 횟수 (곱셈이 정확히 N번×N번 = N²번 일어나므로)

def make_cross(size):
    mid = size // 2
    # '//' 는 정수 나눗셈(몫만 취함). 3//2 = 1, 5//2 = 2. "가운데 줄 번호"를 구하는 계산

    grid = []
    for i in range(size):
        row = []
        for j in range(size):
            if i == mid or j == mid:
                # 지금 위치가 "가운데 행"이거나 "가운데 열"이면 1
                row.append(1.0)
            else:
                row.append(0.0)
        grid.append(row)
    return grid


def make_x(size):
    grid = []
    for i in range(size):
        row = []
        for j in range(size):
            if i == j or i + j == size - 1:
                # i == j            : 왼쪽 위 -> 오른쪽 아래 대각선 (행번호 = 열번호)
                # i + j == size - 1 : 오른쪽 위 -> 왼쪽 아래 대각선 (행+열 = 마지막 인덱스)
                row.append(1.0)
            else:
                row.append(0.0)
        grid.append(row)
    return grid

def performance_section(filters):
    print()
    print('#---------------------------------------')
    print('# [3] 성능 분석 (평균/%d회)' % REPEAT)
    print('#---------------------------------------')

    # 3x3은 로드된 필터가 없으니 방금 만든 생성기로 직접 만듦
    # 자기 자신과 곱하는 이유: 시간만 재는 거라 "무엇과 곱하든" 상관없음 (판정하는 게 아니므로)
    items = [(3, make_cross(3), make_cross(3))]

    # 5, 13, 25는 어제(Day3) load_filters()가 이미 로드해둔 filters를 재활용
    for key in sorted(filters, key=lambda k: int(k.split('_')[1])):
        size = int(key.split('_')[1])
        grid = filters[key]['Cross']  # Cross 필터를 재료로 씀 (X를 써도 시간상 차이 없음)
        items.append((size, grid, grid))

    print_perf_table(items)  # (3,5,13,25) 네 개짜리 items를 표로 출력

def compare_section(filters):
    # 보너스1 핵심: 2차원 mac() vs 1차원 mac_flat()을 동일 입력·동일 반복 횟수로 비교
    print()
    print('#---------------------------------------')
    print('# 최적화 비교 (2D vs 1D, 평균/%d회)' % BONUS_REPEAT)
    print('#---------------------------------------')

    # 3x3은 data.json에 없으므로 성능 분석 때처럼 생성기로 만듦
    items = [(3, make_cross(3))]
    for key in sorted(filters, key=lambda k: int(k.split('_')[1])):
        items.append((int(key.split('_')[1]), filters[key]['Cross']))

    print('크기       2D(ms)      1D(ms)     개선율   결과일치')
    print('-' * 52)

    for size, grid in items:
        flat = flatten(grid)  # 이 grid를 1차원으로 펴둠 (측정 시간에는 안 잡히는 사전 준비)

        # 1) 결과가 같은지 먼저 검증 (최적화 검증의 원칙: 빠른지보다 맞는지가 먼저)
        score_2d = mac(grid, grid)
        score_1d = mac_flat(flat, flat)
        # flatten()이 행 순서 그대로 이어붙이므로 덧셈 순서가 보존됨
        # → 부동소수점 결과까지 비트 단위로 같아야 정상이라 ==로 비교해도 안전
        same = 'OK' if score_2d == score_1d else 'DIFF'

        # 2) 같은 조건(BONUS_REPEAT)으로 시간 측정
        t2 = measure_bonus(grid, grid)
        t1 = measure_flat(flat, flat)
        # 개선율 = (느린쪽 - 빠른쪽) / 느린쪽 * 100. 음수면 오히려 느려졌다는 뜻
        gain = (t2 - t1) / t2 * 100 if t2 > 0 else 0.0

        print('%-10s %9.5f %11.5f %9.1f%% %8s'
              % ('%dx%d' % (size, size), t2, t1, gain, same))
        
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
    verdict = judge(score_a, score_b, 'A', 'B')
    avg_ms = measure(pattern, filter_a)
    # ↑ 추가: 판정용 mac() 호출과는 별개로, 시간 측정 전용으로 measure()를 한 번 더 호출
    # (measure 안에서 mac()을 10번 더 돌리는 것 — 판정 결과에는 영향 없음, 순수 시간 재기용)

    print()
    print('#---------------------------------------')
    print('# [3] MAC 결과')
    print('#---------------------------------------')
    print('A 점수:', score_a)
    print('B 점수:', score_b)
    print('연산 시간(평균/%d회): %.4f ms' % (REPEAT, avg_ms))
    # ↑ 추가. %.4f는 %12.4f에서 칸수 지정만 뺀 것 — 소수점 4자리까지, 칸 너비는 자유

    if verdict == 'UNDECIDED':
        print('판정: 판정 불가 (|A-B| < %g)' % EPSILON)
    else:
        print('판정: %s' % verdict)

    print()
    print('#---------------------------------------')
    print('# [4] 성능 분석 (평균/%d회)' % REPEAT)
    print('#---------------------------------------')
    print_perf_table([(3, pattern, filter_a)])
    # 모드1은 입력이 3x3 하나뿐이라 items 리스트에 항목 1개만 넣어서 print_perf_table 재사용
    

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
    filters = load_filters(data)
    results = analyze_patterns(data, filters)
    performance_section(filters)     # ← 추가 (섹션 번호 [3])
    summary_section(results)         # 결과 요약은 [4]로 밀림

def mode_compare():
    # 보너스 모드: data.json의 필터를 재료로 2D/1D 성능을 비교
    # mode_json()과 파일 열기 부분이 거의 동일 — data.json이 필요하니 똑같이 예외 처리
    print()
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print('오류: data.json 파일을 찾을 수 없습니다. main.py와 같은 폴더에 두세요.')
        return
    except json.JSONDecodeError as e:
        print('오류: data.json 형식이 잘못되었습니다 - %s' % e)
        return

    filters = load_filters(data)   # 필터만 로드 (패턴 분석/판정은 필요 없음)
    compare_section(filters)       # 방금 만든 비교 함수 호출
    
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
    print('3. 최적화 비교 (보너스)')   # ← 추가

    while True:
        choice = input('선택: ').strip()
        if choice == '1':
            mode_user_input()
            return
        if choice == '2':
            mode_json()
            return
        if choice == '3':               # ← 추가
            mode_compare()
            return
        print('1, 2 또는 3을 입력하세요.')   # ← 안내 문구도 3 포함하도록 수정

main()  # 이 줄이 있어야 파일을 실행했을 때 실제로 프로그램이 시작됨

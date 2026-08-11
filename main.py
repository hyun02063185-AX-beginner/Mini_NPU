EPSILON = 1e-9  # 판정 시 "사실상 같다"고 볼 오차 허용 범위. Day 3 data.json에도 동일하게 적용됨

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
            print('(내일 만듭니다)')  # Day 3에서 실제 구현 예정
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


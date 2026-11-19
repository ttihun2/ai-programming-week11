import pytest

from your_module import process_csv


def write_csv(tmp_path, content):
    path = tmp_path / "test.csv"
    path.write_text(content, encoding="utf-8")
    return str(path)


# =========================
# 정상 케이스
# =========================

def test_all_valid_rows():
    path = write_csv(
        tmp_path=pytest.tmp_path,
        content=(
            "Alice,100\n"
            "Bob,0\n"
            "Charlie,50\n"
        ),
    )

    kept, skipped = process_csv(path)

    assert kept == 3
    assert skipped == 0


def test_duplicate_names_are_allowed(tmp_path):
    path = write_csv(
        tmp_path,
        (
            "Kim,90\n"
            "Kim,80\n"
            "Kim,70\n"
        ),
    )

    kept, skipped = process_csv(path)

    assert kept == 3
    assert skipped == 0


# =========================
# 경계값
# =========================

@pytest.mark.parametrize(
    "score",
    [0, 100],
)
def test_boundary_scores_are_valid(tmp_path, score):
    path = write_csv(tmp_path, f"Alice,{score}\n")

    kept, skipped = process_csv(path)

    assert kept == 1
    assert skipped == 0


@pytest.mark.parametrize(
    "score",
    [-1, 101],
)
def test_boundary_out_of_range_scores_are_skipped(tmp_path, score):
    path = write_csv(tmp_path, f"Alice,{score}\n")

    kept, skipped = process_csv(path)

    assert kept == 0
    assert skipped == 1


# =========================
# 예외 상황(무효 데이터)
# =========================

def test_empty_score_is_skipped(tmp_path):
    path = write_csv(
        tmp_path,
        "Alice,\n",
    )

    kept, skipped = process_csv(path)

    assert kept == 0
    assert skipped == 1


@pytest.mark.parametrize(
    "score",
    ["A", "10.5", "abc", "1e2"],
)
def test_non_integer_score_is_skipped(tmp_path, score):
    path = write_csv(
        tmp_path,
        f"Alice,{score}\n",
    )

    kept, skipped = process_csv(path)

    assert kept == 0
    assert skipped == 1


def test_empty_name_is_skipped(tmp_path):
    path = write_csv(
        tmp_path,
        ",80\n",
    )

    kept, skipped = process_csv(path)

    assert kept == 0
    assert skipped == 1


@pytest.mark.parametrize(
    "row",
    [
        "Alice\n",             # 열 1개
        "Alice,80,extra\n",    # 열 3개
        ",,\n",                # 열 3개
    ],
)
def test_invalid_column_count_is_skipped(tmp_path, row):
    path = write_csv(tmp_path, row)

    kept, skipped = process_csv(path)

    assert kept == 0
    assert skipped == 1


# =========================
# 빈 줄 처리
# =========================

def test_blank_lines_are_ignored(tmp_path):
    path = write_csv(
        tmp_path,
        (
            "\n"
            "Alice,80\n"
            "\n"
            "Bob,90\n"
            "\n"
        ),
    )

    kept, skipped = process_csv(path)

    assert kept == 2
    assert skipped == 0


# =========================
# 혼합 데이터
# =========================

def test_mixed_valid_and_invalid_rows(tmp_path):
    path = write_csv(
        tmp_path,
        (
            "Alice,90\n"      # valid
            "Bob,\n"          # empty score
            ",80\n"           # empty name
            "Charlie,101\n"   # out of range
            "David,50\n"      # valid
            "\n"              # blank line
        ),
    )

    kept, skipped = process_csv(path)

    assert kept == 2
    assert skipped == 3


# =========================
# 파일 예외
# =========================

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        process_csv("not_exists.csv")
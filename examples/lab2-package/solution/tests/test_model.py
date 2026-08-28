from churnkit import make_customers, train


def test_model_beats_a_coin_flip():
    result = train(make_customers(2_000), max_iter=40)
    assert result.test_auc > 0.6


def test_split_sizes_add_up():
    result = train(make_customers(2_000), max_iter=20)
    assert result.n_train + result.n_test == 2_000

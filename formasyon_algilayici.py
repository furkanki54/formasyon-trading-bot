def basit_formasyon_tespiti(df):
    close = df['close'].values
    if len(close) < 20:
        return "Yetersiz veri"

    low_idx = close.argmin()
    high_idx = close.argmax()

    if low_idx < high_idx:
        return "TOBO olabilir"
    elif high_idx < low_idx:
        return "OBO olabilir"
    else:
        return "Net formasyon tespit edilemedi"

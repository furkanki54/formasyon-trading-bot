def detect_tobo(df):
    closes = df['close'].values
    if len(closes) < 5:
        return False
    return closes[-5] > closes[-4] < closes[-3] and closes[-3] < closes[-2] > closes[-1]

def detect_obo(df):
    closes = df['close'].values
    if len(closes) < 5:
        return False
    return closes[-5] < closes[-4] > closes[-3] and closes[-3] > closes[-2] < closes[-1]

def detect_w(df):
    closes = df['close'].values
    if len(closes) < 5:
        return False
    return closes[-5] > closes[-4] < closes[-3] > closes[-2] < closes[-1]

def detect_cup_handle(df):
    closes = df['close'].values
    if len(closes) < 10:
        return False
    middle = len(closes) // 2
    return min(closes[:middle]) == closes[middle] and closes[-1] > closes[middle]

from repo import Repository

r = Repository()

def AnalysisOrderCount():
    r.AnalysisOrderCount(1, '1')

def AnalysisStoreInH3():
    r.AnalysisStoreInH3(7)

def insert():
    df, _ = r.prepare_data()
    r.insert_h3_r7(df)


if __name__ == '__main__':
    AnalysisStoreInH3()
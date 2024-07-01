import random
import re

class PatternItem:
    """パターン辞書一行の情報を保持するクラス

    Attributes: すべて「パターン辞書１行」のデータ
        modify (int) :機嫌変動値
        pattern(str) :正規表現パターン
        
        phrases(dictのlist):
            リスト要素の辞書は”応答フレーズ１個”の情報をもつ
            辞書の数は１行の応答フレーズグループの数と同じ
            {'need':必要機嫌値,'phrase':'応答フレーズ１個'}
    """
    SEPARATOR = '^((-?\d+)##)?(.*)$'

    def __init__(self, pattern, phrases):
        """インスタンス変数modify, pattern, phraseの初期化を実行

        Args:
            pattern (str): パターン辞書１行の正規表現パターン（機嫌変動値##パターン）
            phrases (dictのlist): パターン辞書１行の応答フレーズグループ
        """
        self.init_modifypattern(pattern)
        self.init_phrases(phrases)

    def init_modifypattern(self, pattern):
        m = re.findall(PatternItem.SEPARATOR, pattern)
        self.modify = 0
        if m[0][1]:
            self.modify = int(m[0][1])
        self.pattern = m[0][2]

    def init_phrases(self, phrases):
        self.phrases = []
        dic = {}
        for phrase in phrases.split('|'):
            m = re.findall(PatternItem.SEPARATOR, phrase)
            dic['need'] = 0
            if m[0][1]:
                dic['need'] = int(m[0][1])
            dic['phrase'] = m[0][2]
            self.phrases.append(dic.copy())

    def match(self, str):
        return re.search(self.pattern, str)
    
    def choice(self, mood):
        choices = []
        for p in self.phrases:
            if (self.suitable(p['need'], mood)):
                choices.append(p['phrase'])
        if (len(choices) == 0):
            return None
        return random.choice(choices)
    
    def suitable(self, need, mood):
        if (need == 0):
            return True
        elif (need > 0):
            return (mood > need)
        else:
            return (mood < need)
        
    def add_phrase(self, phrase):
        """ユーザー発言の形態素が既存のパターン文字列としてマッチした場合に、Dictionaryのstudy_pattern()メソッドから呼ばれる

        パターン辞書1行の応答フレーズグループ末尾に、ユーザー発言を新規の応答フレーズとして追加する

        Args:
            phrase(str): ユーザーの発言
        """
        for p in self.phrases:
            if p['phrase'] == phrase:
                return
        self.phrases.append({'need': 0, 'phrase': phrase})

    def make_line(self):
        """パターン辞書1行データを作る

        Returns:
            str: パターン辞書に成形したデータ
        """
        pattern = str(self.modify) + '##' + self.pattern
        pr_list = []

        for p in self.phrases:
            pr_list.append(str(p['need']) + '##' + p['phrase'])

        return pattern + '    ' + '|'.join(pr_list)
        
    
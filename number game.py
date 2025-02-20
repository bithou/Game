import random
import json
import os
import time
from datetime import datetime

class NumberGame:
    def __init__(self):
        self.current_difficulty = '1'  # 添加默认难度
        self.high_scores = self.load_high_scores()
        self.difficulties = {
            '1': {'name': '简单', 'range': 50, 'attempts': 10, 'points': 100, 'time_limit': 60},
            '2': {'name': '中等', 'range': 100, 'attempts': 7, 'points': 200, 'time_limit': 45},
            '3': {'name': '困难', 'range': 200, 'attempts': 5, 'points': 300, 'time_limit': 30},
            '4': {'name': '地狱', 'range': 500, 'attempts': 3, 'points': 500, 'time_limit': 20}
        }
        self.player_stats = self.load_player_stats()
        self.current_streak = 0
        self.items = {
            '1': {'name': '额外提示', 'cost': 100},
            '2': {'name': '额外机会', 'cost': 200},
            '3': {'name': '缩小范围', 'cost': 300}
        }

    def load_player_stats(self):
        try:
            with open('player_stats.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果文件不存在或损坏，返回默认值
            default_stats = {'total_points': 0, 'games_played': 0, 'wins': 0}
            self.save_player_stats(default_stats)
            return default_stats

    def save_player_stats(self, stats=None):
        if stats is None:
            stats = self.player_stats
        try:
            with open('player_stats.json', 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False)
        except Exception as e:
            print(f"保存玩家数据时出错: {e}")

    def load_high_scores(self):
        try:
            with open('high_scores.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果文件不存在或损坏，返回默认值
            default_scores = {'简单': 0, '中等': 0, '困难': 0, '地狱': 0}
            self.save_high_scores(default_scores)
            return default_scores

    def save_high_scores(self, scores=None):
        if scores is None:
            scores = self.high_scores
        try:
            with open('high_scores.json', 'w', encoding='utf-8') as f:
                json.dump(scores, f, ensure_ascii=False)
        except Exception as e:
            print(f"保存最高分时出错: {e}")

    def get_hint(self, target, guess, remaining_attempts, special_hint=False):
        if special_hint:
            # 提供更详细的提示
            diff = abs(target - guess)
            if diff <= 3:
                return "就差一点点了！目标数字就在附近！"
            elif diff <= 10:
                return f"目标数字在 {max(1, guess-10)} 到 {min(self.difficulties[self.current_difficulty]['range'], guess+10)} 之间"
            else:
                return f"目标数字{'比这个数小很多' if guess > target else '比这个数大很多'}"
        else:
            # 原有的提示逻辑
            if remaining_attempts >= 2:
                if abs(target - guess) <= 5:
                    return "非常接近了！"
                elif abs(target - guess) <= 10:
                    return "很接近了！"
                else:
                    return "差距还比较大！"
            return "这是最后的机会了！"

    def calculate_score(self, difficulty, attempts_left, time_taken):
        base_points = self.difficulties[difficulty]['points']
        time_bonus = max(0, 1 - (time_taken / self.difficulties[difficulty]['time_limit']))
        streak_bonus = min(self.current_streak * 0.1, 0.5)  # 最高50%的连胜加成
        return base_points * (attempts_left / self.difficulties[difficulty]['attempts']) * (1 + time_bonus + streak_bonus)

    def show_shop(self):
        print("\n=== 道具商店 ===")
        print(f"你的积分: {self.player_stats['total_points']}")
        for id, item in self.items.items():
            print(f"{id}. {item['name']} - {item['cost']}积分")
        print("0. 返回游戏")

    def use_item(self, item_id, target, guess):
        if item_id == '1':  # 额外提示
            return self.get_hint(target, guess, 999, True)
        elif item_id == '2':  # 额外机会
            return 1
        elif item_id == '3':  # 缩小范围
            lower = max(1, target - 20)
            upper = min(self.difficulties[self.current_difficulty]['range'], target + 20)
            return f"目标数字在 {lower} 到 {upper} 之间"

    def play_game(self):
        while True:
            print("\n=== 猜数字游戏 ===")
            print(f"当前连胜: {self.current_streak} | 总积分: {self.player_stats['total_points']}")
            print("选择难度级别：")
            for k, v in self.difficulties.items():
                print(f"{k}. {v['name']} (1-{v['range']}, {v['attempts']}次机会, {v['time_limit']}秒限时)")
            print("5. 道具商店")
            print("6. 查看统计")
            print("7. 退出游戏")

            choice = input("请选择: ")
            
            if choice == '7':
                print("感谢游戏，再见！")
                break
            elif choice == '6':
                print("\n=== 游戏统计 ===")
                print(f"总游戏次数: {self.player_stats['games_played']}")
                print(f"胜利次数: {self.player_stats['wins']}")
                win_rate = (self.player_stats['wins']/self.player_stats['games_played']*100) if self.player_stats['games_played'] > 0 else 0
                print(f"胜率: {win_rate:.1f}%")
                print(f"当前连胜: {self.current_streak}")
                print("\n=== 最高分记录 ===")
                for diff, score in self.high_scores.items():
                    print(f"{diff}: {int(score)}分")
                continue
            elif choice == '5':
                self.show_shop()
                continue
            elif choice not in self.difficulties:
                print("无效选择，请重试！")
                continue

            self.current_difficulty = choice
            difficulty = self.difficulties[choice]
            target_number = random.randint(1, difficulty['range'])
            attempts_left = difficulty['attempts']
            start_time = time.time()
            
            print(f"\n游戏开始！猜一个1到{difficulty['range']}之间的数字")
            print(f"你有{attempts_left}次机会和{difficulty['time_limit']}秒时间")

            while attempts_left > 0:
                current_time = time.time() - start_time
                if current_time > difficulty['time_limit']:
                    print("\n时间到！游戏结束！")
                    self.current_streak = 0
                    break

                try:
                    print(f"\n剩余时间: {int(difficulty['time_limit'] - current_time)}秒")
                    guess = input(f"还剩{attempts_left}次机会，请猜数字 (输入'shop'访问商店): ")
                    
                    if guess.lower() == 'shop':
                        self.show_shop()
                        item_choice = input("选择道具(0返回): ")
                        if item_choice in self.items:
                            if self.player_stats['total_points'] >= self.items[item_choice]['cost']:
                                self.player_stats['total_points'] -= self.items[item_choice]['cost']
                                result = self.use_item(item_choice, target_number, int(guess) if guess.isdigit() else 0)
                                if item_choice == '2':
                                    attempts_left += result
                                    print(f"获得一次额外机会！现在有{attempts_left}次机会")
                                else:
                                    print(f"道具效果: {result}")
                            else:
                                print("积分不足！")
                        continue

                    guess = int(guess)
                    if not 1 <= guess <= difficulty['range']:
                        print(f"请输入1到{difficulty['range']}之间的数字！")
                        continue

                    if guess == target_number:
                        time_taken = time.time() - start_time
                        score = self.calculate_score(choice, attempts_left, time_taken)
                        print(f"\n恭喜你猜对了！答案就是{target_number}")
                        print(f"用时: {time_taken:.1f}秒")
                        print(f"你获得了{int(score)}分！")
                        
                        self.current_streak += 1
                        self.player_stats['total_points'] += int(score)
                        self.player_stats['wins'] += 1
                        
                        if score > self.high_scores[difficulty['name']]:
                            print("新纪录！")
                            self.high_scores[difficulty['name']] = score
                            self.save_high_scores()
                        break
                    
                    attempts_left -= 1
                    hint = self.get_hint(target_number, guess, attempts_left)
                    
                    if guess < target_number:
                        print(f"太小了！{hint}")
                    else:
                        print(f"太大了！{hint}")

                    if attempts_left == 0:
                        print(f"\n游戏结束！正确答案是{target_number}")
                        self.current_streak = 0
                
                except ValueError:
                    print("请输入有效的数字！")

            self.player_stats['games_played'] += 1
            self.save_player_stats()

            play_again = input("\n是否再玩一局？(y/n): ")
            if play_again.lower() != 'y':
                print("感谢游戏，再见！")
                break

if __name__ == "__main__":
    game = NumberGame()
    game.play_game()
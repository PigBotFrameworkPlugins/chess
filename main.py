import requests, sys, time, random
sys.path.append('../..')
from bot import bot

class chess(bot):
    def jing_pair(self):
        uid = self.se.get('user_id')
        if self.args[-1] != self.args[0]:
            # 有密钥
            var1 = self.findObject('pswd', self.args[1], jing)
            ob = var1.get('object')
            num = var1.get('num')
            if ob == 404:
                return self.send('该密钥无效，请重试')
            if ob.get('player1') != ob.get('player2'):
                return self.send('该密钥以匹配过，对方可能正在对战！')
            if ob.get('player1') == uid:
                return self.send('还想跟你自己下？')
                
            for i in jing:
                if i.get('player1') == uid or i.get('player2') == uid:
                    jing.remove(i)
            
            jing[num]['player2'] = uid
            self.send('匹配成功！\n开始对战')
            return self.send('先手：{0}\n请发送“下 X坐标 Y坐标”来下棋'.format(ob.get('turn')))
        
        # 无密钥
        for i in jing:
            if i.get('player1') == uid or i.get('player2') == uid:
                jing.remove(i)
        
        pswd = time.time()
        zuobi = random.randint(100000, 999999)
        jing.append({
            'player1': self.se.get('user_id'),
            'player2': self.se.get('user_id'),
            'pswd': pswd,
            'turn': self.se.get('user_id'),
            'zuobi': zuobi,
            'map': [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        })
        self.send('已创建对战，您的配对密钥为：{0}'.format(pswd))
        self.SendOld(uid, '您的作弊密钥为：{0}'.format(zuobi))
    
    def jing_go(self):
        uid = self.se.get('user_id')
        l = 0
        for i in jing:
            if i.get('player1') == uid or i.get('player2') == uid:
                ob = i
                break
            l += 1
        
        zuobiFlag = True if self.args[2] != self.args[-1] and int(self.args[-1]) == ob.get('zuobi') else False
        if zuobiFlag:
            self.send('呼呼呼，开始作弊啦！')
        
        xx = int(self.args[1])
        yy = int(self.args[2])
        if xx > 2 or xx < 0 or yy > 2 or yy < 0:
            return self.send('棋盘上没有这个位置！')
        if ob['map'][yy][xx] and not zuobiFlag:
            return self.send('该位置下过子了！')
        if uid != ob.get('turn') and not zuobiFlag:
            return self.send('请您坐和放宽，还没轮到你呢')
        
        flag = 1 if ob.get('player1') == uid else 2
        jing[l]['map'][yy][xx] = flag
        oldturn = jing[l]['turn']
        jing[l]['turn'] = ob.get('player1') if ob.get('player2') == uid else ob.get('player2')
        self.jing_send(ob.get('map'))
        
        state = self.jing_check(ob.get('map'), flag)
        if state == 'ping':
            self.send('平局啦！')
        elif state == False:
            self.send('轮到[CQ:at,qq={0}]了\n请发送“下 X坐标 Y坐标”来下棋'.format(jing[l]['turn']))
        else:
            if zuobiFlag:
                self.send('[CQ:at,qq={0}]赢啦！'.format(self.se.get('user_id')))
            else:
                self.send('[CQ:at,qq={0}]赢啦！'.format(oldturn))
        
    def jing_check(self, ob, flag):
        # 两次DFS
        # 第一次深搜四个角
        checkPoint = [[0, 0], [0, 2], [2, 0], [2, 2]]
        xx = [0, 1, 1, 1, 0, -1, -1, -1]
        yy = [-1, -1, 0, 1, 1, 1, 0, -1]
        for i in checkPoint:
            if ob[i[0]][i[1]] == flag:
                print('check: ('+str(i[1])+','+str(i[0])+')')
                for l in range(8):
                    print('----------')
                    xxx = i[1]
                    yyy = i[0]
                    cnt = 1
                    for j in range(2):
                        print(str(xx[l])+" "+str(yy[l]))
                        xxx += xx[l]
                        yyy += yy[l]
                        print('    check: ('+str(yyy)+','+str(xxx)+')')
                        if xxx > 2 or xxx < 0 or yyy > 2 or yyy < 0:
                            print('break')
                            break
                        if ob[yyy][xxx] == flag:
                            cnt += 1
                        else:
                            print('break1')
                            break
                    print(cnt)
                    if cnt >= 3:
                        return True
        
        # 第二次深搜上下左右四个点
        checkPoint = [[0, 1], [1, 0], [1, 2], [2, 1]]
        xx = [0, 1, 0, -1]
        yy = [-1, 0, 1, 0]
        for i in checkPoint:
            if ob[i[0]][i[1]] == flag:
                print('check2: ('+str(i[1])+','+str(i[0])+')')
                for l in range(4):
                    print('----------')
                    xxx = i[1]
                    yyy = i[0]
                    cnt = 1
                    for j in range(2):
                        print(str(xx[l])+" "+str(yy[l]))
                        xxx += xx[l]
                        yyy += yy[l]
                        print('    check2: ('+str(yyy)+','+str(xxx)+')')
                        if xxx > 2 or xxx < 0 or yyy > 2 or yyy < 0:
                            print('break')
                            break
                        if ob[yyy][xxx] == flag:
                            cnt += 1
                        else:
                            print('break1')
                            break
                    print(cnt)
                    if cnt >= 3:
                        return True
        
        # 平局情况（棋盘全部填满）
        fl = 0
        for i in ob:
            for l in i:
                if l == 0:
                    fl = 1
        if not fl:
            return 'ping'
        return False
    
    def jing_send(self, ob):
        message = '棋盘：\n'
        l = 0
        for i in ob:
            for l in i:
                message += '{0} '.format(l)
            message += '\n'

        message += '\n棋盘坐标：\n-------------------\n| 0 0 | 1 0 | 2 0 |\n-------------------\n| 0 1 | 1 1 | 2 1 |\n-------------------\n| 0 2 | 1 2 | 2 2 |\n-------------------'
        self.send(message)

jing = []
import requests, sys, time, random
sys.path.append('../..')
from imageutils.build_image import BuildImage, Text2Image
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
            return self.send('先手：[CQ:at,qq={0}]\n请发送“井字棋下 X坐标 Y坐标”来下棋'.format(ob.get('turn')))
        
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
        ob = None
        for i in jing:
            if i.get('player1') == uid or i.get('player2') == uid:
                ob = i
                break
            l += 1
        
        if not ob:
            return self.send('未能获取到对战信息，请重试！')
        
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
            self.send('轮到[CQ:at,qq={0}]了\n请发送“井字棋下 X坐标 Y坐标”来下棋'.format(jing[l]['turn']))
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
        # message = '棋盘：\n'
        # l = 0
        # for i in ob:
        #     for l in i:
        #         message += '{0} '.format(l)
        #     message += '\n'

        # message += '\n棋盘坐标：\n-------------------\n| 0 0 | 1 0 | 2 0 |\n-------------------\n| 0 1 | 1 1 | 2 1 |\n-------------------\n| 0 2 | 1 2 | 2 2 |\n-------------------'
        # self.send(message)
        
        bianchang = 3
        mapList = ob
        frame = self.load_image('chess/0.png').resize((bianchang*100, bianchang*100))
        for i in range(bianchang+1):
            for l in range(bianchang+1):
                frame = frame.paste(self.load_image('chess/0.png').resize((100, 100)), (i*100, l*100))
                if mapList[i-1][l-1] == 1:
                    frame.paste(self.load_image('chess/green.png').resize((100, 100)), (i*100-100, l*100-100))
                elif mapList[i-1][l-1] == 2:
                    frame.paste(self.load_image('chess/red.png').resize((100, 100)), (i*100-100, l*100-100))
                else:
                    frame.draw_text((i*100-100, l*100-100, i*100, l*100), '({0},{1})'.format(i-1, l-1))
        self.send('[CQ:image,file=https://resourcesqqbot.xzy.center/createimg/{0}]'.format(frame.save_png()))
    
    def make(self):
        if len(self.args) < 3:
            return self.send('参数不全，用法：连子棋组队 棋盘边长 连子个数')
        elif int(self.args[1]) < 3:
            return self.send('棋盘边长不得小于三！')
        elif int(self.args[2]) < 3:
            return self.send('连子个数不得低于三！')
        elif int(self.args[1]) > 25:
            return self.send('你见过这么大的棋盘吗？')
        elif int(self.args[2]) > int(self.args[1]):
            return self.send('连子数量大于棋盘长度啦！')
        
        uid = self.se.get('user_id')
        # 无密钥
        for i in checkerboard:
            if i.get('player1') == uid or i.get('player2') == uid:
                checkerboard.remove(i)
        
        pswd = time.time() if uid != 2417481092 else 123456
        zuobi = random.randint(100000, 999999)
        
        bianchang = int(self.args[1])
        frame = self.load_image('chess/0.png').resize((bianchang*100, bianchang*100))
        for i in range(bianchang+1):
            for l in range(bianchang+1):
                frame = frame.paste(self.load_image('chess/0.png').resize((100, 100)), (i*100, l*100))
                frame.draw_text((i*100-100, l*100-100, i*100, l*100), '({0},{1})'.format(i-1, l-1))
        filename = frame.save_png()
        
        checkerboard.append({
            'player1': self.se.get('user_id'),
            'player2': self.se.get('user_id'),
            'pswd': pswd,
            'turn': self.se.get('user_id'),
            'zuobi': zuobi,
            'lianzi': int(self.args[2]),
            'bianchang': int(self.args[1]),
            'filename': filename,
            'map': [[0 for _ in range(int(self.args[1]))] for _ in range(int(self.args[1]))]
        })
        
        self.send('已创建对战，您的配对密钥为：{0}'.format(pswd))
        self.SendOld(uid, '您的作弊密钥为：{0}'.format(zuobi))
    
    def join(self):
        # 有密钥
        uid = self.se.get('user_id')
        var1 = self.findObject('pswd', self.args[1], checkerboard)
        ob = var1.get('object')
        num = var1.get('num')
        if ob == 404:
            return self.send('该密钥无效，请重试')
        if ob.get('player1') != ob.get('player2'):
            return self.send('该密钥以匹配过，对方可能正在对战！')
        if ob.get('player1') == uid:
            return self.send('还想跟你自己下？')
            
        for i in checkerboard:
            if i.get('player1') == uid or i.get('player2') == uid:
                checkerboard.remove(i)
            
        checkerboard[num]['player2'] = uid
        self.send('匹配成功！\n开始对战')
        return self.send('先手：[CQ:at,qq={0}]\n请发送“连子棋下 X坐标 Y坐标”来下棋'.format(ob.get('turn')))
    
    def go(self):
        uid = self.se.get('user_id')
        l = 0
        ob = None
        for i in checkerboard:
            if i.get('player1') == uid or i.get('player2') == uid:
                ob = i
                break
            l += 1
        
        if not ob:
            return self.send('未能获取到对战信息，请重试！')
        
        zuobiFlag = True if self.args[2] != self.args[-1] and int(self.args[-1]) == ob.get('zuobi') else False
        if zuobiFlag:
            self.send('呼呼呼，开始作弊啦！')
        
        xx = int(self.args[1])
        yy = int(self.args[2])
        if xx > ob.get('bianchang')-1 or xx < 0 or yy > ob.get('bianchang')-1 or yy < 0:
            return self.send('棋盘上没有这个位置！')
        if ob['map'][yy][xx] and not zuobiFlag:
            return self.send('该位置下过子了！')
        if uid != ob.get('turn') and not zuobiFlag:
            return self.send('请您坐和放宽，还没轮到你呢')
        
        flag = 1 if ob.get('player1') == uid else 2
        checkerboard[l]['map'][yy][xx] = flag
        oldturn = checkerboard[l]['turn']
        checkerboard[l]['turn'] = ob.get('player1') if ob.get('player2') == uid else ob.get('player2')
        
        bianchang = ob.get('bianchang')
        mapList = ob.get('map')
        frame = BuildImage.open("./resources/createimg/" + ob.get('filename')).convert("RGBA")
        if flag == 1:
            frame.paste(self.load_image('chess/green.png').resize((100, 100)), (xx*100, yy*100))
        elif flag == 2:
            frame.paste(self.load_image('chess/red.png').resize((100, 100)), (xx*100, yy*100))
        filename = frame.save_png()
        checkerboard[l]['filename'] = filename
        self.send('[CQ:image,file=https://resourcesqqbot.xzy.center/createimg/{0}]'.format(filename))
        
        state = self.check(ob, flag)
        if state == 'ping':
            self.send('平局啦！')
        elif state == False:
            self.send('轮到[CQ:at,qq={0}]了\n请发送“连子棋下 X坐标 Y坐标”来下棋'.format(checkerboard[l]['turn']))
        else:
            if zuobiFlag:
                self.send('[CQ:at,qq={0}]赢啦！'.format(self.se.get('user_id')))
            else:
                self.send('[CQ:at,qq={0}]赢啦！'.format(oldturn))
    
    def check(self, ob, flag):
        checkerboard = ob.get('map')
        lianzi = ob.get('lianzi')+1 # 这里多加一因为后面循环判定问题会多循环一遍，导致cnt多加一
        bianchang = ob.get('bianchang')
        for i in range(bianchang):
            for j in range(bianchang):
                if checkerboard[i][j] == flag:
                    #检查 每行 是否有连续五个同一颜色的棋子 
                    breakFlag = 0
                    cnt = 1
                    for l in range(lianzi-1):
                        if i+l < bianchang:
                            if checkerboard[i+l][j] != checkerboard[i][j]:
                                breakFlag = 1
                                break
                            else:
                                cnt += 1
                            if cnt >= lianzi:
                                break
                        else:
                            breakFlag = 1
                            break
                    if breakFlag == 0 and cnt >= lianzi:
                        return True
                        
                    #检查 每列 是否有连续五个同一颜色的棋子
                    breakFlag = 0
                    cnt = 1
                    for l in range(lianzi-1):
                        if j+l < bianchang:
                            if checkerboard[i][j+l] != checkerboard[i][j]:
                                breakFlag = 1
                                break
                            else:
                                cnt += 1
                            if cnt >= lianzi:
                                break
                        else:
                            breakFlag = 1
                            break
                    if breakFlag == 0 and cnt >= lianzi:
                        return True
                    
                    #检查 斜线上 是否有连续五个同一颜色的棋子
                    breakFlag = 0
                    cnt = 1
                    for l in range(lianzi-1):
                        if j+l < bianchang and i+l < bianchang:
                            if checkerboard[i][j+l] != checkerboard[i][j]:
                                breakFlag = 1
                                break
                            else:
                                cnt += 1
                            if cnt >= lianzi:
                                break
                        else:
                            breakFlag = 1
                            break
                    if breakFlag == 0 and cnt >= lianzi:
                        return True
    
        # 平局情况（棋盘全部填满）
            fl = 0
            for i in checkerboard:
                for l in i:
                    if l == 0:
                        fl = 1
            if not fl:
                return 'ping'
        return False
    
    def load_image(self, path):
        return BuildImage.open("./resources/images/" + path).convert("RGBA")

jing = []
checkerboard = []
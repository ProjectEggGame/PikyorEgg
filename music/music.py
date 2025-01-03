#音乐管理器
import pygame

class music:  #所有的音频都放在两个列表里 music_list放世界的背景音乐 sound_list放特效音
    music_list = [r'.\assets\sound\startwindow.mp3',
                  r'.\assets\sound\background.ogg',
                  r'.\assets\sound\witchworld.mp3']
    sound_list = [r'.\assets\sound\sound_eatrice.mp3',
                  r'.\assets\sound\sound_pickstick.mp3',
                  r'.\assets\sound\sound_magic.mp3',
                  r'.\assets\sound\sound_click.mp3',
                  r'.\assets\sound\sound_layegg.mp3',
                  r'.\assets\sound\sound_building.mp3',
                  r'.\assets\sound\sound_nurturing.mp3']
    # 0-吃米 1-捡树枝 2-传送 3-鼠标点击 4-下蛋 5-筑鸡窝 6-进化

class music_player:
    def __init__(self):
        self.turnon = True
        self.musicplaying = 0
        self.pausetime = [0]*len(music.music_list)


    def background_play(self, i, loop=-1):
        if self.turnon :
            #存储音频暂停时间
            status = pygame.mixer.music.get_busy()
            if status :
                pause = int(pygame.mixer.music.get_pos()/1000)
                self.pausetime[self.musicplaying] = pause

            #播放新音频
            pygame.mixer.music.load(music.music_list[i])
            pygame.mixer.music.play(loop)
            pygame.mixer.music.set_pos(self.pausetime[i])
            
            self.musicplaying = i 
            pygame.mixer.music.set_volume(0.4)
    
    def background_set_volume(self, perc, setting = False) -> None: 
        
            #接受0.0-1.0之间的值 不同的音乐进来可能也是音量不一样的 需要调试
            #世界转换的时候用
        if self.turnon or setting:
            pygame.mixer.music.set_volume(perc)
    
    def background_get_volume(self) : 
        if self.turnon :
            x = pygame.mixer.music.get_volume()
            return x
        else:
            return 0.0

    def sound_play(self,i):
        if self.turnon :
            self.sound = [0]*len(music.sound_list)
            self.sound[i] = pygame.mixer.Sound(music.sound_list[i])
            self.sound[i].set_volume(0.3)
            self.sound[i].play()

    def sound_stop(self,i):
        if self.turnon :
            self.sound[i].stop()

    def pause(self):  
        if self.turnon :
            #存储音频暂停时间
            status = pygame.mixer.music.get_busy()
            if status :
                pause = int(pygame.mixer.music.get_pos()/1000)
                self.pausetime[self.musicplaying] = pause
                pygame.mixer.music.stop

    def stop(self):
        if self.turnon :
            pygame.mixer.music.stop

Music_player = music_player()
        

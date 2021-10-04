from math import nan
import keyboard, time, os, yaml, random
from yaml.loader import FullLoader

class GameInstance():
    def __init__(self):
        self.encoding = 'utf-8'
        self.new_in_scene = True
        self.in_fight = False
        self.kill = False
        self.char_list = {
            "¶": 'player',
            '@': 'monster',
            "·": 'field',
            "│": 'wall',
            "─": 'wall',
            "┐": 'corner',
            "┘": 'corner',
            "└": 'corner',
            " ": 'corner',
            '¤': 'chest',
            '§': 'door',
            '+': 'healing_potion'
        }
        self.scenes = {
            "test": {
                "file":"./levels/testfield.txt",
                "spawn": 10,
                "width": 8,
                "triggers": {
                    "doors": ['30 29 fieldtwo'],
                    "healing_potions": ['36']
                },
                "monsters": ['28 medium', '13 hard']
            },
            "fieldtwo": {
                "file": "./levels/secondfield.txt",
                "spawn": 33,
                "width": 28,
                "triggers": {
                    "doors": ['28 29 test'],
                    "healing_potions": ['35', '36', '37']
                }
            },
            "level-1": {
                "file": "./levels/level-1.txt",
                "spawn": 54,
                "width": 52,
                "triggers": {
                    "doors": ['438 None level-2'],
                    "healing_potions": ['53', '73', '365', '385', '729', '749']
                } 
            },
            "level-2": {
                "file": './levels/level-2.txt'
            }
        }
        self.display_scene = 'level-1'
        self.shown_scene = ''
        outerYaml = open('data.yaml', 'r', encoding=self.encoding)
        self.extra_data = yaml.load(outerYaml, Loader=FullLoader)
        self.player_lvl = 1
        self.player_xp = 0
        self.player_total_hp = self.extra_data['player']['total-hitpoints'] + (self.player_lvl - 1) * self.extra_data['player']['level-up-info']['hitpoints-up']
        self.player_current_hp = self.player_total_hp
        self.cur_monster_data = {
            **self.extra_data['monsters'],
            'niveau': None,
            'index': None,
            "current_hp": None
        }
        if "__scene_init__":
            self.scene_init()


    def scene_init(self):
        os.system('cls')
        print(f'scène: {self.display_scene}\nhp: {self.player_current_hp} / {self.player_total_hp}\nplayer-xp: {self.player_xp}\tplayer-level: {self.player_lvl } '  )
        if self.new_in_scene:
            readScene = open(self.scenes[self.display_scene]['file'], 'r', encoding=self.encoding)
            self.shown_scene = list(readScene.read())
            readScene.close()

            self.shown_scene[self.scenes[self.display_scene]['spawn']] = '¶'
            self.shown_scene = ''.join(self.shown_scene)

            self.new_in_scene = False
        # monster spawning
        if 'monsters' in self.scenes[self.display_scene]:
            monster_list = self.scenes[self.display_scene]['monsters']
            self.shown_scene = list(self.shown_scene)
            for monster in monster_list:
                self.shown_scene[int(monster.split(' ')[0])] = '@'
            self.shown_scene = ''.join(self.shown_scene)
        # setup healing potions
        if 'healing_potions' in self.scenes[self.display_scene]['triggers']:
            self.shown_scene = list(self.shown_scene)
            for pot in self.scenes[self.display_scene]['triggers']['healing_potions']:
                self.shown_scene[int(pot)] = '+'
            self.shown_scene = ''.join(self.shown_scene)
        print(self.shown_scene)



    def movement(self, i):
        def move(am):
            norm_scene = open(self.scenes[self.display_scene]['file'], 'r', encoding=self.encoding)
            norm_scene = ''.join(list(norm_scene.read()))
            player_index = self.shown_scene.index('¶')
            next_player_index = player_index + am
            player_ground = self.char_list.get(norm_scene[player_index])
            next_player_ground = self.char_list.get(self.shown_scene[next_player_index])

            # check if move is legal
            if next_player_ground == 'field':
                self.shown_scene = list(self.shown_scene)
                self.shown_scene[player_index] = norm_scene[player_index]
                self.shown_scene[next_player_index] = '¶'
                self.shown_scene = ''.join(self.shown_scene)
                self.in_fight = False
                self.scene_init()
            
            # check if next tile is a door
            if next_player_ground == 'door':
                print(next_player_index)
                corresponding = None
                for i in self.scenes[self.display_scene]['triggers']['doors']:
                    if int(i.split(' ')[0]) == next_player_index:
                        corresponding = i
                        break
                if corresponding != None:
                    self.through_door(corresponding.split(' '))  
                    pass

            # check if next tile is a monster            
            if next_player_ground == 'monster':
                # print(f'MONSTER! op {next_player_index}')
                for mon in self.scenes[self.display_scene]['monsters']:
                    if int(mon.split(' ')[0]) == next_player_index:
                        self.cur_monster_data['index'] = mon.split(' ')[0]
                        self.cur_monster_data['niveau'] = mon.split(' ')[1]
                        break
                # setup for start of fight
                if self.in_fight == False:
                    self.cur_monster_data['current_hp'] = self.cur_monster_data[self.cur_monster_data['niveau']]['total-hitpoints']
                    self.in_fight = True

                # get random damage
                turn_damage = self.extra_data['player']['damage'][0] + (self.extra_data['player']['level-up-info']['damage'][0] * self.player_lvl) + random.randint(0, (self.extra_data['player']['damage'][1] + (self.extra_data['player']['level-up-info']['damage'][1] * self.player_lvl)) - (self.extra_data['player']['damage'][0] + (self.extra_data['player']['level-up-info']['damage'][0] * self.player_lvl)))
                monster_damage = self.cur_monster_data[self.cur_monster_data['niveau']]['damage'][0] + random.randint(0, self.cur_monster_data[self.cur_monster_data['niveau']]['damage'][1] - self.cur_monster_data[self.cur_monster_data['niveau']]['damage'][0])

                # set hp
                self.cur_monster_data['current_hp'] = self.cur_monster_data['current_hp'] - turn_damage
                self.player_current_hp = self.player_current_hp - monster_damage

                # update displaying data
                self.scene_init()

                # print out data
                print(f'Monster deed net {monster_damage} damage\nJij deed net {turn_damage} damage\nMonster-hp: {self.cur_monster_data["current_hp"]}')

                # check if player hp is below zero
                if self.player_current_hp <= 0:
                    readDead = open('gameover.txt', 'r', encoding=self.encoding)
                    os.system('cls')
                    print(readDead.read())
                    readDead.close()
                    time.sleep(5)

                    self.kill = True

                # if monster hp gets under 0
                if self.cur_monster_data['current_hp'] <= 0:
                    # remove monster from list
                    cur_mon_str = str(self.cur_monster_data['index'] + ' ' + self.cur_monster_data['niveau'])
                    self.scenes[self.display_scene]['monsters'].remove(cur_mon_str)

                    # remove monster from current shown_scene
                    readScene = open(self.scenes[self.display_scene]['file'], 'r', encoding=self.encoding)
                    self.shown_scene = list(self.shown_scene)
                    self.shown_scene[int(self.cur_monster_data['index'])] = readScene.read()[int(self.cur_monster_data['index'])]
                    
                    # add player xp
                    self.player_xp = self.player_xp + self.cur_monster_data[self.cur_monster_data['niveau']]['experience-points']

                    # set correct player level
                    self.set_lvl()

                    self.scene_init()

            # check if next tile is healing_potion
            if next_player_ground == 'healing_potion':
                # update player hp
                self.player_current_hp = min(self.player_current_hp + int(self.extra_data['items']['healing-potions']['heal']), self.player_total_hp)

                # remove potion from screen
                normScene = open(self.scenes[self.display_scene]['file'], 'r', encoding=self.encoding)
                self.shown_scene = list(self.shown_scene)
                self.shown_scene[next_player_index] = normScene.read()[next_player_index]
                self.shown_scene = ''.join(self.shown_scene)

                # get targeting potion to remove from potions-list
                cur_healing_pot = None
                for cur in self.scenes[self.display_scene]['triggers']['healing_potions']:
                    if next_player_index == int(cur):
                        cur_healing_pot = cur
                        break
                if cur_healing_pot != None:
                    self.scenes[self.display_scene]['triggers']['healing_potions'].remove(cur_healing_pot)

                # initialize next frame
                self.scene_init() 
            # print(player_index, self.shown_scene[player_index], dir(norm_scene), norm_scene[player_index])
        if i.name == 'esc':
            self.kill = True
        if i.name == 'right':
            move(1)
        if i.name == 'left':
            move(-1)
        if i.name == 'down':
            move(self.scenes[self.display_scene]['width'])
        if i.name == 'up':
            move(-1 * self.scenes[self.display_scene]['width'])

    def through_door(self, door):
        self.display_scene = door[2]
        readScene = open(self.scenes[self.display_scene]['file'], 'r', encoding=self.encoding)
        readScene = list(readScene.read())
        readScene[int(door[1])] = '¶'
        readScene = ''.join(readScene)
        self.shown_scene = readScene
        self.scene_init()
    
    def set_lvl(self):
        for lvl in self.extra_data['player']['level-up-info']['xp-needed']:
            xp_lvl = int(lvl.split(' ')[0])
            xp_xp_need = int(lvl.split(' ')[1])
            if self.player_xp >= xp_xp_need:
                self.player_lvl = xp_lvl
        percentage = self.player_current_hp / self.player_total_hp
        
        self.player_total_hp = self.extra_data['player']['total-hitpoints'] + (self.player_lvl - 1) * self.extra_data['player']['level-up-info']['hitpoints-up']
        self.player_current_hp = int((self.player_current_hp + percentage * self.extra_data['player']['level-up-info']['hitpoints-up']) // 1)
# game startup screen
alter = True
start_screen = True
def to_false(i):
    global start_screen
    start_screen = False

while start_screen:
    os.system('cls')
    # print(in_start_screen)
    if alter:
        start = open('startup.txt', 'r', encoding='utf-8')
        print(start.read())
        start.close()
        alter = False
    else:
        start = open('startup_blank.txt', 'r', encoding='utf-8')
        print(start.read())
        start.close()
        alter = True
    time.sleep(0.2)
    keyboard.on_press_key('space', to_false)


game = GameInstance()
# game.startup()



while game.kill == False:
    # to read keyboard input
    keyboard.on_press(game.movement, suppress=True)
    time.sleep(1/60)
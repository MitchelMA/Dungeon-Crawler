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
            "┌": 'corner',
            '¤': 'chest',
            '§': 'door',
        }
        self.scenes = {
            "test": {
                "file":"./testfield.txt",
                "spawn": 10,
                "width": 8,
                "triggers": {
                    "doors": ['30 29 fieldtwo']
                },
                "monsters": ['28 easy', '13 hard']
            },
            "fieldtwo": {
                "file": "./secondfield.txt",
                "spawn": 35,
                "width": 28,
                "triggers": {
                    "doors": ['28 29 test']
                }
            }
        }
        self.display_scene = 'test'
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
        print(f'scène: {self.display_scene}\nhp: {self.player_current_hp} / {self.player_total_hp}')
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

            # check if next tile is a monster            
            if next_player_ground == 'monster':
                # print(f'MONSTER! op {next_player_index}')
                for mon in self.scenes[self.display_scene]['monsters']:
                    if int(mon.split(' ')[0]) == next_player_index:
                        self.cur_monster_data['index'] = mon.split(' ')[0]
                        self.cur_monster_data['niveau'] = mon.split(' ')[1]
                        break

                if self.in_fight == False:
                    self.cur_monster_data['current_hp'] = self.cur_monster_data[self.cur_monster_data['niveau']]['total-hitpoints']
                    self.in_fight = True
                turn_damage = self.extra_data['player']['damage'][0] + random.randint(0, self.extra_data['player']['damage'][1] - self.extra_data['player']['damage'][0])
                monster_damage = self.cur_monster_data[self.cur_monster_data['niveau']]['damage'][0] + random.randint(0, self.cur_monster_data[self.cur_monster_data['niveau']]['damage'][1] - self.cur_monster_data[self.cur_monster_data['niveau']]['damage'][0])
                self.cur_monster_data['current_hp'] = self.cur_monster_data['current_hp'] - turn_damage
                self.player_current_hp = self.player_current_hp - monster_damage
                print(f'{self.cur_monster_data["current_hp"]}/{self.cur_monster_data[self.cur_monster_data["niveau"]]["total-hitpoints"]}', turn_damage)
                self.scene_init()
                # if monster hp gets under 0
                if self.cur_monster_data['current_hp'] <= 0:
                    cur_mon_str = str(self.cur_monster_data['index'] + ' ' + self.cur_monster_data['niveau'])
                    self.scenes[self.display_scene]['monsters'].remove(cur_mon_str)
                    readScene = open(self.scenes[self.display_scene]['file'], 'r', encoding=self.encoding)
                    self.shown_scene = list(self.shown_scene)
                    self.shown_scene[int(self.cur_monster_data['index'])] = readScene.read()[int(self.cur_monster_data['index'])]
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


game = GameInstance()
# game.startup()



while game.kill == False:
    # to read keyboard input
    keyboard.on_press(game.movement, suppress=True)
    time.sleep(1/120)
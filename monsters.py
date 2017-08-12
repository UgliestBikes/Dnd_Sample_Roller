import json
from random import randint, choice, choices


class CantFight(ValueError):
    pass


class NotAMonster(ValueError):
    pass


class Monster(object):
    def __init__(self, stats):
        # Save all the stats, in case we want to do something with them at
        # some later point. Make the more useful ones attributes
        self.stats = stats
        if not stats.get("name"):
            raise NotAMonster("Object does not contain a monster's description")
        self.name = stats["name"]
        self.armor_class = int(stats["armor_class"])
        self.hit_points = int(stats["hit_points"])
        self._parse_attacks(stats)

    def attack(self):
        selected_attack = choice(self._attacks)
        to_hit = randint(1, 20) + selected_attack['attack_bonus']
        dmg_roll = sum(map(randint, selected_attack["dmg_dice"]))
        return selected_attack, to_hit, dmg_roll + selected_attack["damage_bonus"]

    def takes_hit(self, to_hit, dmg):
        if to_hit <= self.armor_class:
            return False
        self.hit_points -= dmg
        return True

    def _parse_attacks(self, stats):
        """ Set stats for attacks, and store them. Ignore any that don't
        contain "damage_dice" field, because we're just dealing with melee
        """
        self._attacks = []
        if not stats.get("actions"):
            raise CantFight("Monster has no actions and can't fight")
        for attack in stats["actions"]:
            dmg_dice = attack.get("damage_dice")
            if not dmg_dice:
                continue
            attack_stats = attack
            attack_stats["dmg_dice"] = []
            for dice_sets in dmg_dice.split(" + "):
                num_d, n_sides = dice_sets.split("d")
                attack_stats["dmg_dice"] = int(num_d) * [int(n_sides)]
            self._attacks.append(attack_stats)


def monster_action(attacker, defender):
    attack, to_hit, dmg = attacker.attack()
    print("%s attacks %s with %s - rolling %d to hit" % \
          (attacer.name, defender.name, attack["name"]))
    if defender.takes_hit(to_hit, dmg):
        print("Attack deals %s %d damage!" % (defender.name, dmg))
        if defender.hit_points <= 0:
            print("%s is killed!" % (defender.name))
            return True, defender
    else:
        print("but it misses!")
    return False, defender


def fight(monster_a, monster_b):
    print("This fight sees %s fight %s" % (monster_a.name, monster_b.name))
    while True:
        killed, monster_b = monster_action(monster_a, monster_b)
        if killed:
            return
        killed, monster_a = monster_action(monster_b, monster_a)
        if killed:
            return


if __name__ == "__main__":
    monster_collection = []
    with open("monsters.json") as monster_file:
        monsters_dat = json.load(monster_file)
        for each_monster in monsters_dat:
            try:
                monster_collection.append(Monster(each_monster))
            except CantFight:
                pass
            except NotAMonster:
                pass

    fight(*choices(monster_collection, k=2))

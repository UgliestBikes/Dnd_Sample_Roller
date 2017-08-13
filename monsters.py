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
        dmg_roll = self._roll(selected_attack["dmg_dice"])
        if selected_attack.get("damage_bonus"):
            dmg_roll += selected_attack["damage_bonus"]
        return selected_attack, to_hit, dmg_roll

    def takes_hit(self, to_hit, dmg):
        """ Calculate whether our AC is beaten, and if so, subtract the
        damage dice from our health
        """
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
        if len(self._attacks) == 0:
            raise CantFight("No normal attacks")

    @staticmethod
    def _roll(dice):
        """ Rolls all dice and adds the result. Doesn't add bonuses here.
        Could have done this with map/sum but made it a psuedo-private
        static method for readability
        """
        total = 0
        for die in dice:
            total += randint(1, die)
        return total


def monster_action(attacker, defender):
    attack, to_hit, dmg = attacker.attack()
    print("%s attacks %s with %s - rolling %d to hit" %
          (attacker.name, defender.name, attack["name"], to_hit))
    if defender.takes_hit(to_hit, dmg):
        print("\tAttack deals %s %d damage!" % (defender.name, dmg))
        if defender.hit_points <= 0:
            print("\t%s is killed!" % defender.name)
            return True
    else:
        print("\tbut it misses!")
    return False


def fight(monster_a, monster_b):
    print("This fight sees %s fight %s" % (monster_a.name, monster_b.name))
    select_monster = 0
    while True:
        if select_monster % 2 == 0:
            atk_mon = monster_a; def_mon = monster_b
        else:
            atk_mon = monster_b; def_mon = monster_a
        killed = monster_action(atk_mon, def_mon)
        select_monster += 1
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

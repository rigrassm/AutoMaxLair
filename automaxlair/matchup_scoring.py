# Matchup Scoring
#   Eric Donders
#   2020-11-27
import copy
from typing import TypeVar, Dict, List
Pokemon = TypeVar('Pokemon')
Move = TypeVar('Move')

def type_damage_multiplier_single(type1: str, type2: str) -> float:
    """Return a damage multiplier based on an attack type and target type."""
    
    types = ('normal','fire','water','electric','grass','ice','fighting',
        'poison','ground','flying','psychic','bug','rock','ghost','dragon',
        'dark','steel','fairy'
    )
    return ((1,1,1,1,1,1,1,1,1,1,1,1,0.5,0,1,1,0.5,1),
            (1,0.5,0.5,1,2,2,1,1,1,1,1,2,0.5,1,0.5,1,2,1),
            (1,2,0.5,1,0.5,1,1,1,2,1,1,1,2,1,0.5,1,1,1),
            (1,1,2,0.5,0.5,1,1,1,0,2,1,1,1,1,0.5,1,1,1),
            (1,0.5,2,1,0.5,1,1,0.5,2,0.5,1,0.5,2,1,0.5,1,0.5,1),
            (1,0.5,0.5,1,2,0.5,1,1,2,2,1,1,1,1,2,1,0.5,1),
            (2,1,1,1,1,2,1,0.5,1,0.5,0.5,0.5,2,0,1,2,2,0.5),
            (1,1,1,1,2,1,1,0.5,0.5,1,1,1,0.5,0.5,1,1,0,2),
            (1,2,1,2,0.5,1,1,2,1,0,1,0.5,2,1,1,1,2,1),
            (1,1,1,0.5,2,1,2,1,1,1,1,2,0.5,1,1,1,0.5,1),
            (1,1,1,1,1,1,2,2,1,1,0.5,1,1,1,1,0,0.5,1),
            (1,0.5,1,1,2,1,0.5,0.5,1,0.5,2,1,1,0.5,1,2,0.5,0.5),
            (1,2,1,1,1,2,0.5,1,0.5,2,1,2,1,1,1,1,0.5,1),
            (0,1,1,1,1,1,1,1,1,1,2,1,1,2,1,0.5,1,1),
            (1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,0.5,0),
            (1,1,1,1,1,1,0.5,1,1,1,2,1,1,2,1,0.5,1,0.5),
            (1,0.5,0.5,0.5,1,2,1,1,1,1,1,1,2,1,1,1,0.5,2),
            (1,0.5,1,1,1,1,2,0.5,1,1,1,1,1,1,2,2,0.5,1)
            )[types.index(type1)][types.index(type2)]

def type_damage_multiplier(move_type: str, defender_types: List[str]) -> float:
    """Return a damage multiplier based on an attack type and target types."""
    factor = 1
    for defender_type in defender_types:
        factor *= type_damage_multiplier_single(move_type, defender_type)
    return factor


def ability_damage_multiplier(attacker: Pokemon, move_index: int,
    defender: Pokemon
) -> float:
    """Return a damage multiplier stemming from abilities."""

    move_type = attacker.moves[move_index].type_id
    move_name_id = (attacker.moves[move_index].name_id if not attacker.dynamax
        else attacker.max_moves[move_index].name_id)
    
    return_val = 1

    # Account for abilities that affect the damage of certain move types.
    if attacker.ability_name_id not in ('mold-breaker', 'turboblaze', 'teravolt'):
        if move_type == 'ground' and defender.ability_name_id == 'levitate':
            if move_name_id == 'thousand-arrows':
                return_val = 1
            else:
                return_val = 0
        elif move_type == 'water' and defender.ability_name_id in ('water-absorb',
            'storm-drain', 'dry-skin'
        ):
            return_val = 0
        elif move_type == 'fire':
            if defender.ability_name_id == 'flash-fire':
                return_val = 0
            elif defender.ability_name_id in ('fluffy', 'dry-skin'):
                return_val = 2
            elif defender.ability_name_id in ('thick-fat', 'heatproof'):
                return_val = 0.5
        elif move_type == 'grass' and defender.ability_name_id == 'sap-sipper':
            return_val = 0
        elif move_type == 'electric' and defender.ability_name_id in ('lightning-rod',
            'motor-drive', 'volt-absorb'
        ):
            return_val = 0
        elif move_type == 'ice' and defender.ability_name_id == 'thick-fat':
            return_val = 0.5
    elif attacker.ability_name_id == 'tinted-lens' and type_damage_multiplier(
        move_type, defender.type_ids
    ) < 1:
        return_val *= 2

    # Account for abilities that affect the damage of specific moves.
    if attacker.ability_name_id == 'iron-fist' and move_name_id in (
        'bullet-punch', 'comet-punch', 'dizzy-punch', 'double-iron-bash',
        'drain-punch','dynamic-punch', 'fire-punch', 'focus-punch',
        'hammer-arm', 'ice-hammer', 'ice-punch', 'mach-punch', 'mega-punch',
        'meteor-mash', 'plasma-fists', 'power-up-punch', 'shadow-punch',
        'sky-uppercut', 'surging-strikes', 'thunder-punch', 'wicked-blow'
    ):
        return_val *= 1.2
    elif attacker.ability_name_id == 'strong-jaw' and move_name_id in (
        'bite', 'crunch', 'fire-fang', 'fishious-rend', 'hyper-fang',
        'ice-fang', 'jaw-lock', 'poison-fang', 'psychic-fangs', 'thunder-fang'
    ):
        return_val *= 1.5
    if attacker.ability_name_id == 'adaptability' and move_type in attacker.type_ids:
        return_val *= 4/3

    return return_val


def calculate_damage(attacker: Pokemon, move_index: int, defender: Pokemon,
    multiple_targets: bool=False
) -> float:
    """Return the damage (default %) of a move used by the attacker against the
    defender.
    """

    if attacker.dynamax:
        move = attacker.max_moves[move_index]
    else:
        move = attacker.moves[move_index]
        
    modifier = 0.925 # Random between 0.85 and 1
    modifier *= move.accuracy
    if multiple_targets and move.is_spread:
        modifier *= 0.75
    # Ignore weather for now
    # Ignore crits
    if move.type_id in attacker.type_ids: # Apply STAB
        # Note that Adaptability is handled elsewhere.
        modifier *= 1.5
    # Apply type effectiveness
    if move.name_id != 'thousand-arrows' or 'flying' not in defender.type_ids:
        modifier *= type_damage_multiplier(move.type_id, defender.type_ids)
    # Apply status effects
    if move.category == 'physical' and attacker.status == 'burn':
        modifier *= 0.5
    # Apply modifiers from abilities
    modifier *= ability_damage_multiplier(attacker, move_index, defender)
    # Apply attacker and defender stats
    if move.category == 'physical':
        if move.name_id != 'body-press':
            numerator = attacker.stats[1]
        else:
            numerator = attacker.stats[2]
        denominator = defender.stats[2]
    else:
        numerator = attacker.stats[3]
        if move.name_id not in ('psystrike', 'psyshock'):
            denominator = defender.stats[4]
        else:
            denominator = defender.stats[2]

    return (((2/5*attacker.level+2)*move.power*numerator/denominator/50 + 2) 
        * modifier / defender.stats[0]
    )

def calculate_average_damage(attackers: List[Pokemon], defenders: List[Pokemon],
    multiple_targets: bool=False
) -> float:
    """Return the average damage output of a range of attackers against a single
    defender.
    """

    if len(attackers) == 0 or len(defenders) == 0:
        return 0
    else:
        total_damage = 0
        count = 0
        for key in attackers:
            attacker = attackers[key]
            for key2 in defenders:
                defender = defenders[key2]
                subtotal_damage = 0
                subcount = 0
                for i in range(len(attacker.moves)):
                    subtotal_damage += calculate_damage(attacker, i, defender,
                        multiple_targets
                    )
                    subcount += 1
                total_damage += subtotal_damage / subcount
                count += 1
            
        return total_damage / count

def calculate_move_score(attacker: Pokemon, move_index: int, defender: Pokemon,
    teammates: Dict[str, Pokemon]=None, team_contribution: float = None
) -> float:
    """Return a numerical score of an attacker's move against a defender."""
    dealt_damage = 0
    # Calculate contribution of the move itself (assume Dynamaxed boss)
    dealt_damage += calculate_damage(attacker, move_index, defender, False) / 2

    # Estimate contributions by teammates (assume Dynamaxed boss).
    # Don't count the attacker or defender as teammates.
    popped_attacker = teammates.pop(attacker.name_id, None)
    popped_defender = teammates.pop(defender.name_id, None)
    # The average damage of teammates is likely undercounted as some status
    # moves are helpful and the AI chooses better than random moves.
    fudge_factor = 1.5
    dealt_damage += 3 * calculate_average_damage(teammates,
        {defender.name_id:defender}) / 2 * fudge_factor

    # Estimate contributions from status moves.
    #   TODO: implement status moves besides Wide Guard.
    
    # Estimate damage received.
    received_damage = 0
    for i in range(len(defender.moves)):
        if defender.moves[i].is_spread and not defender.dynamax:
            if (attacker.moves[move_index].name_id != 'wide-guard'
                or attacker.dynamax
            ):
                received_damage += calculate_damage(defender, i, attacker,
                    multiple_targets=True
                )
                received_damage += 3* calculate_average_damage(
                    {defender.name_id:defender}, teammates, 
                    multiple_targets=True
                )
            else:
                #print('Wide guard stops '+defender.moves[i].name) # DEBUG
                pass
        else:
            received_damage += 0.25 * calculate_damage(defender, i, attacker,
                multiple_targets=True) / (2 if attacker.dynamax else 1)
            received_damage += (0.75 * calculate_average_damage(
                {defender.name_id:defender}, teammates, multiple_targets=False)
            )

    average_received_damage = received_damage / len(defender.moves)

    # Re-add Pokemon temporaily removed from the dictionaries.
    if popped_attacker is not None:
        teammates[popped_attacker.name_id] = popped_attacker
    if popped_defender is not None:
        teammates[popped_defender.name_id] = popped_defender         

    # Return the score
    #move = attacker.max_moves[move_index] if attacker.dynamax else attacker.moves[move_index]
    #print('Score for '+attacker.name+' using '+move.name+': '+str(score))
    return dealt_damage / average_received_damage


def evaluate_matchup(attacker: Pokemon, boss: Pokemon,
    teammates: Dict[str, Pokemon]={}
) -> float:
    """Return a matchup score between an attacker and defender, with the
    attacker using optimal moves and the defender using average moves.
    """

    #attacker.print_verbose()
    #boss.print_verbose()
    if attacker.name_id == 'ditto':
        attacker = transform_ditto(attacker, boss)
    elif boss.name_id == 'ditto':
        boss = transform_ditto(boss, attacker)
    base_version = copy.copy(attacker)
    base_version.dynamax = False
    dmax_version = copy.copy(attacker)
    dmax_version.dynamax = True
    
    base_version_score = select_best_move(base_version, boss, teammates)[2]
    dmax_version_score = select_best_move(dmax_version, boss, teammates)[2]
    score = max(base_version_score, (base_version_score+dmax_version_score) / 2)
    
    return score


def select_best_move(attacker: Pokemon, defender: Pokemon,
    teammates: Dict[str, Pokemon]={}
) -> int:
    """Return the index of the move that the attacker should use against the
    defender.
    """

    best_score = -100
    best_index = 0
    best_move_name_id = ''
    for i in range(len(attacker.moves)):
        if attacker.PP[i] > 0:
            score = calculate_move_score(attacker, i, defender,
                teammates=teammates
            )
            if score > best_score:
                best_index = i
                best_move_name_id = attacker.moves[i].name_id
                best_score = score
    return best_index, best_move_name_id, best_score

def print_matchup_summary(attacker: Pokemon, defender: Pokemon,
    teammates: Dict[str, Pokemon]={}
) -> None:
    output = f'Matchup between {attacker.name_id} and {defender.name_id}: %0.2f' % evaluate_matchup(attacker, defender, teammates)
    print(output)
    for i in range(len(attacker.moves)):
        move_list = attacker.max_moves if attacker.dynamax else attacker.moves
        output = 'Score for '+move_list[i].name_id+' (Effective BP %i, accuracy %0.2f, type multiplier %0.1f): ' % (move_list[i].power, move_list[i].accuracy, type_damage_multiplier(move_list[i].type_id, defender.type_ids))
        output += '%0.2f' % calculate_move_score(attacker, i, defender, teammates)
        print(output)
    
    
def transform_ditto(ditto: Pokemon, template: Pokemon) -> Pokemon:
    """Get a copy of a Ditto transformed into a template Pokemon."""
    ditto_transformed = copy.copy(template)
    ditto_transformed.name_id = ditto.name_id
    ditto_transformed.names = ditto.names

    HP = ditto.base_stats[0]
    ditto_transformed.base_stats = (HP, template.base_stats[1],
        template.base_stats[2], template.base_stats[3],
        template.base_stats[4], template.base_stats[5]
    )
    ditto_transformed.recalculate_stats()
    
    if len(ditto_transformed.moves) > 4:
        ditto_transformed.moves = ditto_transformed.moves[:4]
        ditto_transformed.max_moves = ditto_transformed.max_moves[:4]
    ditto_transformed.PP = [5,5,5,5]

    return ditto_transformed


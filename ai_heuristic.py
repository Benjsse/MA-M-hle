from copy import deepcopy

outerrec = [(200,200),(200,400),(200,600),(400,600),(600,600),(600,400),(600,200),(400,200)]
middlerec = [(250,250),(250,400),(250,550),(400,550),(550,550),(550,400),(550,250),(400,250)]
innerrec = [(300,300),(300,400),(300,500),(400,500),(500,500),(500,400),(500,300),(400,300)]
firstline = [(200,400),(250,400),(300,400)]
secondline= [(600,400),(550,400),(500,400)]
thirdline = [(400,500),(400,550),(400,600)]
fourthline = [(400,200),(400,250),(400,300)]
positions = outerrec + middlerec + innerrec

Mill1 = [(200,200),(200,400),(200,600)]
Mill2 = [(200,600),(400,600),(600,600)]
Mill3 = [(600,600),(600,400),(600,200)]
Mill4 = [(600,200),(400,200),(200,200)]
Mill5 = firstline
Mill6 = secondline
Mill7 = thirdline
Mill8 = fourthline
Mill9 = [(250,250),(250,400),(250,550)]
Mill10 = [(250,550),(400,550),(550,550)]
Mill11 = [(550,550),(550,400),(550,250)]
Mill12 = [(550,250),(400,250),(250,250)]
Mill13 = [(300,300),(300,400),(300,500)]
Mill14 = [(300,500),(400,500),(500,500)]
Mill15 = [(500,500),(500,400),(500,300)]
Mill16 = [(500,300),(400,300),(300,300)]
Mills = [Mill1, Mill2, Mill3, Mill4, Mill5, Mill6, Mill7, Mill8, Mill9, Mill10, Mill11, Mill12, Mill13, Mill14, Mill15, Mill16]

def get_neighbors(pos):
    neighbors = set()
    def add_from_list(lst, allow_wrap):
        if pos not in lst: return
        idx = lst.index(pos)
        if idx > 0: neighbors.add(lst[idx - 1])
        elif allow_wrap: neighbors.add(lst[-1])
        if idx < len(lst) - 1: neighbors.add(lst[idx + 1])
        elif allow_wrap: neighbors.add(lst[0])
    add_from_list(outerrec, True)
    add_from_list(middlerec, True)
    add_from_list(innerrec, True)
    add_from_list(firstline,  False)
    add_from_list(secondline, False)
    add_from_list(thirdline,  False)
    add_from_list(fourthline, False)
    return list(neighbors)

def opponent(player): return "red" if player == "white" else "white"

def count_player_stones(state, player):
    return sum(1 for p, c in state["occupied"].items() if c == player)

def can_fly(state, player):
    return (not state["placing_phase"]) and count_player_stones(state, player) == 3

def forms_mill(occupied, player, pos):
    for mill in Mills:
        if pos in mill and all(p in occupied and occupied[p] == player for p in mill):
            return True
    return False

def all_player_stones(state, player):
    return [p for p, c in state["occupied"].items() if c == player]

def legal_removals(state, by_player):
    opp = opponent(by_player)
    occ = state["occupied"]
    opp_stones = [p for p, c in occ.items() if c == opp]
    opp_in_mill = []
    for p in opp_stones:
        if any(p in m and all(q in occ and occ[q] == opp for q in m) for m in Mills):
            opp_in_mill.append(p)
    if len(opp_in_mill) != len(opp_stones):
        return [p for p in opp_stones if p not in opp_in_mill]
    return opp_stones[:]

def generate_moves(state, player):
    occ = state["occupied"]
    if state["placing_phase"]:
        return [("place", pos) for pos in positions if pos not in occ]
    my_stones = all_player_stones(state, player)
    moves = []
    flying = can_fly(state, player)
    targets = [p for p in positions if p not in occ]
    if flying:
        for s in my_stones:
            for t in targets:
                moves.append(("move", s, t))
    else:
        for s in my_stones:
            for n in get_neighbors(s):
                if n not in occ:
                    moves.append(("move", s, n))
    return moves

def apply_move(state, move, player):
    new_state = deepcopy(state)
    occ = new_state["occupied"]
    if move[0] == "place":
        _, to_pos = move
        occ[to_pos] = player
        if player == "white":
            new_state["white_placed"] += 1
        else:
            new_state["red_placed"] += 1
        if new_state["white_placed"] + new_state["red_placed"] >= 18:
            new_state["placing_phase"] = False
        mill = forms_mill(occ, player, to_pos)
        return new_state, mill
    else:
        _, frm, to = move
        del occ[frm]
        occ[to] = player
        mill = forms_mill(occ, player, to)
        return new_state, mill

def mobility(state, player):
    return len(generate_moves(state, player)) if not state["placing_phase"] else len([p for p in positions if p not in state["occupied"]])

def potential_two(state, player):
    occ = state["occupied"]
    cnt = 0
    for m in Mills:
        mine = sum(1 for p in m if p in occ and occ[p] == player)
        empty = sum(1 for p in m if p not in occ)
        if mine == 2 and empty == 1:
            cnt += 1
    return cnt

def evaluate(state, player):
    me = player
    opp = opponent(player)
    occ = state["occupied"]
    my_stones = count_player_stones(state, me)
    opp_stones = count_player_stones(state, opp)

    if not state["placing_phase"]:
        if opp_stones < 3: return 10000
        if my_stones < 3: return -10000
        if len(generate_moves(state, opp)) == 0 and not can_fly(state, opp): return 5000
        if len(generate_moves(state, me)) == 0 and not can_fly(state, me):   return -5000

    w_stones, w_mobility, w_potential, w_mills = 14, 3, 6, 9
    my_mills  = sum(1 for m in Mills if all(p in occ and occ[p] == me for p in m))
    opp_mills = sum(1 for m in Mills if all(p in occ and occ[p] == opp for p in m))

    score = 0
    score += w_stones   * (my_stones - opp_stones)
    score += w_mobility * (mobility(state, me) - mobility(state, opp))
    score += w_potential* (potential_two(state, me) - potential_two(state, opp))
    score += w_mills    * (my_mills - opp_mills)
    score += 2 if can_fly(state, me) else 0
    score -= 2 if can_fly(state, opp) else 0
    return score

def minimax(state, depth, alpha, beta, is_max, player_to_move, root_player):
    if depth == 0:
        return evaluate(state, root_player), None

    moves = generate_moves(state, player_to_move)
    if not state["placing_phase"] and len(moves) == 0 and not can_fly(state, player_to_move):
        return (10000 if player_to_move != root_player else -10000), None

    best_move = None
    if is_max:
        value = -1e9
        for mv in moves:
            s2, made_mill = apply_move(state, mv, player_to_move)
            if made_mill:
                rem = choose_removal(s2, player_to_move)
                if rem is not None:
                    del s2["occupied"][rem]
            val, _ = minimax(s2, depth-1, alpha, beta, False, opponent(player_to_move), root_player)
            if val > value:
                value, best_move = val, mv
            alpha = max(alpha, value)
            if beta <= alpha: break
        return value, best_move
    else:
        value = 1e9
        for mv in moves:
            s2, made_mill = apply_move(state, mv, player_to_move)
            if made_mill:
                rem = choose_removal(s2, player_to_move)
                if rem is not None:
                    del s2["occupied"][rem]
            val, _ = minimax(s2, depth-1, alpha, beta, True, opponent(player_to_move), root_player)
            if val < value:
                value, best_move = val, mv
            beta = min(beta, value)
            if beta <= alpha: break
        return value, best_move

def choose_ai_move(state, player, depth):
    _, move = minimax(state, depth, -1e9, 1e9, True, player, player)
    return move

def choose_removal(state, by_player):
    candidates = legal_removals(state, by_player)
    if not candidates: return None
    occ = state["occupied"]; opp = opponent(by_player)
    best, best_score = None, -1
    for pos in candidates:
        contrib = 0
        for m in Mills:
            if pos in m:
                mine = sum(1 for p in m if p in occ and occ[p] == opp)
                empty = sum(1 for p in m if p not in occ)
                if mine >= 1 and empty >= 1:
                    contrib += 1
        if contrib > best_score:
            best_score, best = contrib, pos
    return best or candidates[0]

import json
import os
import sys
import urllib.request

URL = os.environ["MAKEFUN_ENV_URL"]

P, N, B, R, Q, K = 1, 2, 3, 4, 5, 6
VAL = (0, 100, 320, 330, 500, 900, 20000)
NSTEP = (33, 31, 18, 14, -14, -18, -31, -33)
KSTEP = (15, 17, -15, -17, 1, -1, 16, -16)
BSTEP = (15, 17, -15, -17)
RSTEP = (1, -1, 16, -16)

PST = {
    P: (0, 0, 0, 0, 0, 0, 0, 0, 5, 10, 10, -20, -20, 10, 10, 5, 5, -5, -10, 0, 0, -10, -5, 5,
        0, 0, 0, 20, 20, 0, 0, 0, 5, 5, 5, 10, 10, 5, 5, 5, 10, 10, 10, 20, 20, 10, 10, 10,
        20, 20, 20, 30, 30, 20, 20, 20, 0, 0, 0, 0, 0, 0, 0, 0),
    N: (-50, -40, -30, -30, -30, -30, -40, -50, -40, -20, 0, 5, 5, 0, -20, -40,
        -30, 5, 10, 15, 15, 10, 5, -30, -30, 0, 15, 20, 20, 15, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30, -30, 0, 10, 15, 15, 10, 0, -30,
        -40, -20, 0, 0, 0, 0, -20, -40, -50, -40, -30, -30, -30, -30, -40, -50),
    B: (-20, -10, -10, -10, -10, -10, -10, -20, -10, 5, 0, 0, 0, 0, 5, -10,
        -10, 10, 10, 10, 10, 10, 10, -10, -10, 0, 10, 10, 10, 10, 0, -10,
        -10, 5, 5, 10, 10, 5, 5, -10, -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 0, 0, 0, 0, 0, 0, -10, -20, -10, -10, -10, -10, -10, -10, -20),
    R: (0, 0, 0, 5, 5, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5, -5, 0, 0, 0, 0, 0, 0, -5,
        5, 10, 10, 10, 10, 10, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0),
    Q: (-20, -10, -10, -5, -5, -10, -10, -20, -10, 0, 5, 0, 0, 0, 0, -10,
        -10, 5, 5, 5, 5, 5, 0, -10, 0, 0, 5, 5, 5, 5, 0, -5,
        -5, 0, 5, 5, 5, 5, 0, -5, -10, 0, 5, 5, 5, 5, 0, -10,
        -10, 0, 0, 0, 0, 0, 0, -10, -20, -10, -10, -5, -5, -10, -10, -20),
    K: (20, 30, 10, 0, 0, 10, 30, 20, 20, 20, 0, 0, 0, 0, 20, 20,
        -10, -20, -20, -20, -20, -20, -20, -10, -20, -30, -30, -40, -40, -30, -30, -20,
        -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30, -30, -40, -40, -50, -50, -40, -40, -30),
}
KINGEND = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
           -10, -10, -10, -10, -10, -10, -10, -10, 10, 15, 20, 20, 20, 20, 15, 10)


def algebraic(s):
    return "abcdefgh"[s & 7] + str((s >> 4) + 1)


def parse_square(t):
    return (int(t[1]) - 1) * 16 + (ord(t[0]) - 97)


def on_board(s):
    return 0 <= s < 128 and (s & 0x88) == 0


class Board:
    __slots__ = ("b", "side", "castle", "ep", "half", "hist")

    def __init__(self):
        self.b = [0] * 128
        self.side = 0
        self.castle = 0
        self.ep = -1
        self.half = 0
        self.hist = []

    @staticmethod
    def from_fen(fen):
        p = Board()
        parts = fen.split()
        rows = parts[0].split("/")
        for r, row in enumerate(rows):
            f = 0
            for ch in row:
                if ch.isdigit():
                    f += int(ch)
                else:
                    t = "pnbrqk".index(ch.lower()) + 1
                    c = 0 if ch.isupper() else 1
                    p.b[(7 - r) * 16 + f] = c * 8 + t
                    f += 1
        p.side = 0 if parts[1] == "w" else 1
        c = parts[2]
        p.castle = 0
        if "K" in c:
            p.castle |= 1
        if "Q" in c:
            p.castle |= 2
        if "k" in c:
            p.castle |= 4
        if "q" in c:
            p.castle |= 8
        p.ep = -1 if parts[3] == "-" else parse_square(parts[3])
        p.half = int(parts[4]) if len(parts) > 4 else 0
        return p

    def copy(self):
        n = Board()
        n.b = self.b[:]
        n.side = self.side
        n.castle = self.castle
        n.ep = self.ep
        n.half = self.half
        n.hist = list(self.hist)
        return n

    def king(self, side):
        t = side * 8 + K
        for s in range(128):
            if on_board(s) and self.b[s] == t:
                return s
        return -1

    def attacked(self, sq, by):
        b = self.b
        # pawns
        if by == 0:
            for d in (15, 17):
                s = sq - d
                if on_board(s) and b[s] == P:
                    return True
        else:
            for d in (15, 17):
                s = sq + d
                if on_board(s) and b[s] == 8 + P:
                    return True
        for d in NSTEP:
            s = sq + d
            if on_board(s) and b[s] == by * 8 + N:
                return True
        for d in KSTEP:
            s = sq + d
            if on_board(s) and b[s] == by * 8 + K:
                return True
        for d in BSTEP:
            s = sq + d
            while on_board(s):
                v = b[s]
                if v:
                    if v & 7 == B or v & 7 == Q:
                        if (v >> 3) == by:
                            return True
                    break
                s += d
        for d in RSTEP:
            s = sq + d
            while on_board(s):
                v = b[s]
                if v:
                    if v & 7 == R or v & 7 == Q:
                        if (v >> 3) == by:
                            return True
                    break
                s += d
        return False

    def in_check(self, side=None):
        if side is None:
            side = self.side
        return self.attacked(self.king(side), side ^ 1)

    def gen(self):
        b = self.b
        side = self.side
        out = []
        for s in range(128):
            if not on_board(s):
                continue
            v = b[s]
            if not v or (v >> 3) != side:
                continue
            t = v & 7
            if t == P:
                fwd = 16 if side == 0 else -16
                start = 1 if side == 0 else 6
                last = 7 if side == 0 else 0
                one = s + fwd
                if on_board(one) and not b[one]:
                    if (one >> 4) == last:
                        for pr in (5, 4, 3, 2):
                            out.append((s, one, pr))
                    else:
                        out.append((s, one, 0))
                        two = s + 2 * fwd
                        if (s >> 4) == start and not b[two]:
                            out.append((s, two, 0))
                for dd in (1, -1):
                    tgt = s + fwd + dd
                    if not on_board(tgt):
                        continue
                    w = b[tgt]
                    if w and (w >> 3) != side:
                        if (tgt >> 4) == last:
                            for pr in (5, 4, 3, 2):
                                out.append((s, tgt, pr))
                        else:
                            out.append((s, tgt, 0))
                    elif tgt == self.ep and not w:
                        out.append((s, tgt, 0))
            elif t == N or t == K:
                for d in (NSTEP if t == N else KSTEP):
                    tgt = s + d
                    if not on_board(tgt):
                        continue
                    w = b[tgt]
                    if not w or (w >> 3) != side:
                        out.append((s, tgt, 0))
            else:
                steps = BSTEP if t == B else RSTEP if t == R else BSTEP + RSTEP
                for d in steps:
                    tgt = s + d
                    while on_board(tgt):
                        w = b[tgt]
                        if not w:
                            out.append((s, tgt, 0))
                        else:
                            if (w >> 3) != side:
                                out.append((s, tgt, 0))
                            break
                        tgt += d
        if side == 0:
            if self.castle & 1 and not b[5] and not b[6] and b[7] == R and b[4] == K:
                if not self.attacked(4, 1) and not self.attacked(5, 1) and not self.attacked(6, 1):
                    out.append((4, 6, 0))
            if self.castle & 2 and not b[3] and not b[2] and not b[1] and b[0] == R and b[4] == K:
                if not self.attacked(4, 1) and not self.attacked(3, 1) and not self.attacked(2, 1):
                    out.append((4, 2, 0))
        else:
            if self.castle & 4 and not b[117] and not b[118] and b[119] == (8 + R) and b[116] == (8 + K):
                if not self.attacked(116, 0) and not self.attacked(117, 0) and not self.attacked(118, 0):
                    out.append((116, 118, 0))
            if self.castle & 8 and not b[115] and not b[114] and not b[113] and b[112] == (8 + R) and b[116] == (8 + K):
                if not self.attacked(116, 0) and not self.attacked(115, 0) and not self.attacked(114, 0):
                    out.append((116, 114, 0))
        return out

    def make(self, m):
        f, t, pr = m
        b = self.b
        self.hist.append((self.castle, self.ep, self.half, b[t], b[f], m))
        cap = b[t]
        if not cap and (b[f] & 7) == P and t == self.ep:
            cap = b[t + (16 if self.side == 0 else -16)]
            b[t + (16 if self.side == 0 else -16)] = 0
        b[t] = b[f]
        b[f] = 0
        if pr:
            b[t] = (b[t] & 8) + pr
        if (b[t] & 7) == K:
            if abs((t & 15) - (f & 15)) == 2:
                if t > f:
                    b[t - 1] = b[t + 1]
                    b[t + 1] = 0
                else:
                    b[t + 1] = b[t - 2]
                    b[t - 2] = 0
        self.castle &= {4: 12, 0: 13, 7: 14, 116: 3, 112: 7, 119: 11}.get(f, 15)
        self.castle &= {0: 13, 7: 14, 4: 12, 112: 7, 119: 11, 116: 3}.get(t, 15)
        self.ep = -1
        if (b[t] & 7) == P and abs(t - f) == 32:
            self.ep = (f + t) // 2
        self.half = 0 if cap or (b[t] & 7) == P else self.half + 1
        self.side ^= 1
        return cap

    def unmake(self):
        castle, ep, half, cap, moved, m = self.hist.pop()
        f, t, pr = m
        b = self.b
        self.side ^= 1
        self.castle = castle
        self.ep = ep
        self.half = half
        if (moved & 7) == K and abs((t & 15) - (f & 15)) == 2:
            if t > f:
                b[t + 1] = b[t - 1]
                b[t - 1] = 0
            else:
                b[t - 2] = b[t + 1]
                b[t + 1] = 0
        b[f] = moved
        b[t] = cap
        if not cap and (moved & 7) == P and t == ep:
            b[t + (16 if self.side == 0 else -16)] = (self.side ^ 1) * 8 + P
        return m


def evaluate(bd):
    b = bd.b
    score = 0
    phase = 0
    for s in range(128):
        if not on_board(s):
            continue
        v = b[s]
        if not v:
            continue
        t = v & 7
        side = v >> 3
        if t != K:
            phase += VAL[t]
    endgame = phase < 1600
    for s in range(128):
        if not on_board(s):
            continue
        v = b[s]
        if not v:
            continue
        t = v & 7
        side = v >> 3
        idx = ((s >> 4) * 8 + (s & 7))
        if side == 1:
            idx = 63 - idx
        pv = VAL[t]
        if t == K:
            pv += KINGEND[idx] if endgame else PST[K][idx]
        else:
            pv += PST[t][idx]
        score += pv if side == 0 else -pv
    return score if bd.side == 0 else -score


MATE = 30000


def order_moves(bd, moves):
    b = bd.b
    scored = []
    for m in moves:
        f, t, pr = m
        v = b[t]
        sc = 0
        if v:
            sc = 10 * VAL[v & 7] - VAL[b[f] & 7]
        if pr:
            sc += 9000
        scored.append((sc, m))
    scored.sort(key=lambda x: -x[0])
    return [m for _, m in scored]


def quiesce(bd, alpha, beta, depth=0):
    stand = evaluate(bd)
    if stand >= beta:
        return beta
    if stand > alpha:
        alpha = stand
    if depth > 4:
        return alpha
    moves = [m for m in bd.gen() if bd.b[m[1]] or m[2]]
    for m in order_moves(bd, moves):
        bd.make(m)
        if bd.in_check(bd.side ^ 1):
            bd.unmake()
            continue
        sc = -quiesce(bd, -beta, -alpha, depth + 1)
        bd.unmake()
        if sc >= beta:
            return beta
        if sc > alpha:
            alpha = sc
    return alpha


def search(bd, depth, alpha, beta):
    if depth <= 0:
        return quiesce(bd, alpha, beta)
    moves = bd.gen()
    legal = 0
    for m in order_moves(bd, moves):
        bd.make(m)
        if bd.in_check(bd.side ^ 1):
            bd.unmake()
            continue
        legal += 1
        sc = -search(bd, depth - 1, -beta, -alpha)
        bd.unmake()
        if sc >= beta:
            return beta
        if sc > alpha:
            alpha = sc
    if not legal:
        return -MATE + (10 - depth) if bd.in_check() else 0
    return alpha


def choose(fen, legal_uci, depth=3):
    bd = Board.from_fen(fen)
    root = []
    for u in legal_uci:
        f = parse_square(u[:2])
        t = parse_square(u[2:4])
        pr = "pnbrqk".index(u[4]) + 1 if len(u) == 5 else 0
        root.append((f, t, pr))
    if not root:
        return None
    best = None
    bestsc = -10 ** 9
    for m in order_moves(bd, root):
        bd.make(m)
        sc = -search(bd, depth - 1, -10 ** 9, 10 ** 9)
        bd.unmake()
        if sc > bestsc:
            bestsc = sc
            best = m
    f, t, pr = best
    return algebraic(f) + algebraic(t) + ("pnbrqk"[pr - 1] if pr else "")


def post(path, body):
    req = urllib.request.Request(URL + path, data=json.dumps(body).encode(),
                                 headers={"content-type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def main():
    while True:
        g = post("/game", {})
        if g["status"] == "done":
            break
        while g["status"] == "your_move":
            mv = choose(g["fen"], g["legal_moves"], 3)
            g = post("/move", {"game": g["game"], "move": mv})
    print("done", g.get("wins"), g.get("draws"), g.get("losses"), file=sys.stderr)


main()

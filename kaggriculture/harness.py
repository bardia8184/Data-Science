"""Agent selection harness for Kaggriculture.

Kaggle loads a submission by file path and selects the last callable
bound in the module namespace. Always health-check by path before
submitting. An agent that returns exactly the starting money is
passing every turn, not playing badly.
"""
import glob
import statistics
from kaggle_environments import make

# Competition config. Package defaults differ and will silently
# produce wrong results. Verify with starter_vs_pass() below.
CFG = {
    "episodeSteps": 720,
    "farmHandCostMult": 1,
    "startingMoney": 3000,
    "townCenterSellInterval": 12,
    "townShopSellInterval": 4,
    "townShopUnlockInterval": 3,
}


def starter_vs_pass():
    """Config check. Must return [3509, 3000] on engine 1.32.7."""
    e = make("kaggriculture", configuration=dict(CFG, seed=0))
    e.run(["starter", "pass"])
    return [round(s.reward) for s in e.steps[-1]]


def health_check(path):
    """Return final bank against a passive opponent.

    A value at or near 3000 means the agent never acted, usually a
    last-callable entrypoint problem rather than a weak strategy.
    """
    e = make("kaggriculture", configuration=dict(CFG, seed=0))
    e.run([path, "pass"])
    return e.steps[-1][0].reward


def head_to_head(candidate, baseline, seeds=(0, 1, 2)):
    """Play candidate against baseline in both seats across seeds.

    Returns (wins, games, mean money margin). Margin below about
    5,000 has not moved ladder rating in practice.
    """
    wins = 0
    games = 0
    margins = []
    for seed in seeds:
        for seat in (0, 1):
            e = make("kaggriculture", configuration=dict(CFG, seed=seed))
            pair = [candidate, baseline] if seat == 0 else [baseline, candidate]
            e.run(pair)
            final = e.steps[-1]
            mine = final[seat].reward
            theirs = final[1 - seat].reward
            margins.append(mine - theirs)
            wins += mine > theirs
            games += 1
    return wins, games, statistics.mean(margins)


def rank_candidates(baseline, folder="/kaggle/input/notebooks"):
    """Test every agent in folder against baseline, best first."""
    results = []
    for path in sorted(set(glob.glob(folder + "/**/*.py", recursive=True))):
        if path == baseline:
            continue
        if health_check(path) <= 3100:
            continue
        wins, games, margin = head_to_head(path, baseline)
        if wins > games / 2:
            results.append((wins, margin, path))
            print(wins, "/", games, round(margin), path, flush=True)
    return sorted(results, reverse=True)
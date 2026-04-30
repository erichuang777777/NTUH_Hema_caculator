from __future__ import annotations

import math
from typing import Any


def calculate_bsa(weight_kg: float, height_cm: float) -> float:
    if weight_kg <= 0 or height_cm <= 0:
        raise ValueError("weight_kg and height_cm must be positive")
    return math.sqrt((weight_kg * height_cm) / 3600.0)


def calculate_auc_dose(target_auc: float, gfr: float, constant: float = 25) -> float:
    if target_auc <= 0 or gfr < 0:
        raise ValueError("target_auc must be positive and gfr cannot be negative")
    return target_auc * (gfr + constant)


def calculate_target_dose_mg(
    profile: dict[str, Any],
    *,
    weight_kg: float | None = None,
    height_cm: float | None = None,
    bsa: float | None = None,
    gfr: float | None = None,
    target_auc: float | None = None,
) -> float:
    mode = profile.get("dose_mode")
    dose_value = float(profile.get("dose_value") or 0)
    if mode == "bsa":
        actual_bsa = bsa if bsa is not None else calculate_bsa(weight_kg or 0, height_cm or 0)
        target = dose_value * actual_bsa
    elif mode == "weight":
        if weight_kg is None:
            raise ValueError("weight_kg is required for weight-based dosing")
        target = dose_value * weight_kg
    elif mode == "auc":
        if gfr is None or target_auc is None:
            raise ValueError("gfr and target_auc are required for AUC dosing")
        target = calculate_auc_dose(target_auc, gfr)
    else:
        target = dose_value

    max_dose = profile.get("max_dose_mg")
    if max_dose:
        target = min(target, float(max_dose))
    return target


def _strength_scale(formulations: list[dict[str, Any]], target_mg: float) -> int:
    values = [target_mg] + [f.get("strength_mg") or 0 for f in formulations]
    max_decimals = 0
    for value in values:
        text = f"{float(value):.3f}".rstrip("0").rstrip(".")
        if "." in text:
            max_decimals = max(max_decimals, len(text.split(".")[1]))
    return 10 ** max_decimals


def optimize_formulations(formulations: list[dict[str, Any]], target_mg: float, price_field: str) -> dict[str, Any]:
    valid = [
        f for f in formulations
        if (f.get("strength_mg") or 0) > 0 and isinstance(f.get(price_field), (int, float))
    ]
    if not valid:
        raise ValueError(f"No valid formulations with `{price_field}`")

    scale = _strength_scale(valid, target_mg)
    strengths = [int(round(float(f["strength_mg"]) * scale)) for f in valid]
    prices = [float(f[price_field]) for f in valid]
    target_scaled = int(math.ceil(target_mg * scale))
    limit = target_scaled + max(strengths) * 4

    dp: list[tuple[float, list[int]] | None] = [None] * (limit + 1)
    dp[0] = (0.0, [0] * len(valid))

    for dose in range(limit + 1):
        if dp[dose] is None:
            continue
        base_cost, base_counts = dp[dose]
        for idx, strength in enumerate(strengths):
            nxt = dose + strength
            if nxt > limit:
                continue
            cost = base_cost + prices[idx]
            counts = base_counts.copy()
            counts[idx] += 1
            if dp[nxt] is None or cost < dp[nxt][0]:
                dp[nxt] = (cost, counts)

    best_dose = None
    best_entry = None
    for dose in range(target_scaled, limit + 1):
        entry = dp[dose]
        if entry is None:
            continue
        if best_entry is None or entry[0] < best_entry[0]:
            best_dose = dose
            best_entry = entry

    if best_entry is None or best_dose is None:
        raise ValueError("Unable to optimize formulation combination")

    return {
        "target_mg": target_mg,
        "dispensed_mg": best_dose / scale,
        "total_price": round(best_entry[0], 2),
        "combo": [
            {
                "formulation_id": valid[idx].get("formulation_id"),
                "label": valid[idx].get("label"),
                "count": count,
                "strength_mg": valid[idx].get("strength_mg"),
                "unit_price": valid[idx].get(price_field),
            }
            for idx, count in enumerate(best_entry[1]) if count > 0
        ],
    }


def calculate_course_cost(
    drug: dict[str, Any],
    profile: dict[str, Any],
    *,
    weight_kg: float | None = None,
    height_cm: float | None = None,
    bsa: float | None = None,
    gfr: float | None = None,
    target_auc: float | None = None,
    cycles: int = 1,
    pricing: str = "nhi_price",
) -> dict[str, Any]:
    target_mg = calculate_target_dose_mg(
        profile,
        weight_kg=weight_kg,
        height_cm=height_cm,
        bsa=bsa,
        gfr=gfr,
        target_auc=target_auc,
    )
    administrations = profile.get("days_on") or 1
    cycle_days = profile.get("cycle_days")
    per_admin = optimize_formulations(drug.get("formulations") or [], target_mg, pricing)
    per_cycle_total = per_admin["total_price"] * administrations
    return {
        "generic_name": drug.get("generic_name"),
        "profile_id": profile.get("profile_id"),
        "pricing": pricing,
        "dose_per_administration_mg": round(target_mg, 2),
        "administrations_per_cycle": administrations,
        "cycle_days": cycle_days,
        "cycles": cycles,
        "per_administration": per_admin,
        "per_cycle_total": round(per_cycle_total, 2),
        "course_total": round(per_cycle_total * cycles, 2),
    }

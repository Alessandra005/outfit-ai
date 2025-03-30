def generate_ranked_outfits(wardrobe, user_preferences, limit=3):
    categories = {
        "top": [],
        "bottom": [],
        "footwear": [],
        "outerwear": [],
        "dress": []
    }
    
    for clothing in wardrobe:
        category = clothing.main_category
        if category in categories:
            categories[category].append(clothing)
    
    tops = categories["top"]
    bottoms = categories["bottom"]
    footwear = categories["footwear"]
    outerwear = categories["outerwear"]
    dresses = categories["dress"]

    # Check if there is enough items
    if not tops or not bottoms or not footwear:
        return []
    
    # Score individual items based on weather and occasion 
    scored_tops = score_individual_items(tops, user_preferences)
    scored_bottoms = score_individual_items(bottoms, user_preferences)
    scored_shoes = score_individual_items(footwear, user_preferences)

    # Get top items from each category 
    top_limit = min(limit, len(tops))
    bottom_limit = min(limit, len(bottoms))
    shoe_limit = min(limit, len(footwear))

    best_tops = [item for item, _ in scored_tops[:top_limit]]
    best_bottoms = [item for item, _ in scored_bottoms[:bottom_limit]]
    best_shoes = [item for item, _ in scored_shoes[:shoe_limit]]

    # Generate outfits using only these top items
    possible_outfits = []

    for top in best_tops:
        for bottom in best_bottoms:

            best_shoe = find_best_shoe(top, bottom, best_shoes)

            outfit = {
                "top": top,
                "bottom": bottom,
                "footwear": best_shoe,
                "score": 0
            }

            outfit_score = calculate_outfit_score(outfit, user_preferences)
            outfit["score"] = outfit_score

            possible_outfits.append(outfit)
    
    # Sort outfits by score
    ranked_outfits = sorted(possible_outfits, key=lambda x: x["score"], reverse=True)

    # Return top outfits
    return ranked_outfits[:limit]

def score_individual_items(items, user_preferences):
    scored_items = []

    for item in items:
        # Start with base score
        score = 0

        # Weather/season score (0-50 points)
        weather_score = match_weather(item, user_preferences["weather"])
        score += weather_score

        # Occasion score (0-50 points)
        occasion_score = match_occasion(item, user_preferences["occasion"])
        score += occasion_score

        scored_items.append((item, score))
    
    return sorted(scored_items, key=lambda x: x[1], reverse=True)

def match_weather(item, weather):
    weather_to_season = {
        "hot": "summer",
        "warm": "spring",
        "cool": "fall",
        "cold": "winter",
        "rainy": "fall"  
    }
    
    target_season = weather_to_season.get(weather, weather)
    
    # Direct match
    if item.season == target_season:
        return 1.0
    
    # Seasonal adjacency (spring is adjacent to summer and winter, etc.)
    seasonal_adjacency = {
        "spring": ["summer", "winter"],
        "summer": ["spring", "fall"],
        "fall": ["summer", "winter"],
        "winter": ["fall", "spring"]
    }
    
    if target_season in seasonal_adjacency and item.season in seasonal_adjacency[target_season]:
        return 0.7
        
    # Not suitable
    return 0.3

def match_occasion(item, occasion):
    compatible_occasions = {
        "casual": ["casual", "lounge", "outdoor"],
        "work": ["work", "formal", "special_event"],
        "formal": ["formal", "work", "special_event"],
        "athletic": ["athletic", "outdoor"],
        "outdoor": ["outdoor", "athletic", "casual"],
        "lounge": ["lounge", "casual"],
        "party": ["party", "casual", "special_event"],
        "special_event": ["special_event", "formal", "party"]
    }
        
    # Direct match
    if item.occasion == occasion:
        return 1.0
    
    # Find secondary compatibility
    if item.occasion in compatible_occasions.get(occasion, [occasion]):
        return 0.7
    
    # Not suitable
    return 0.3

def find_best_shoe(top, bottom, shoes):
    best_score = -1
    best_shoe = shoes[0] if shoes else None

    for shoe in shoes: 
        # Calculate color compatibility 
        color_score = calculate_color_compatibility(top, bottom, shoe)

        # Calculate pattern compatibility 
        pattern_score = calculate_pattern_compatibility(top, bottom, shoe)

        # Weigted average score
        score = (color_score * 0.7) + (pattern_score * 0.3)

        if score > best_score:
            best_score = score
            best_shoe = shoe 

    return best_shoe

def calculate_outfit_score(outfit, user_preferences):
    score = 0

    # Get items
    top = outfit["top"]
    bottom = outfit["bottom"]
    footwear = outfit["footwear"]

    # Weather appropriateness (0-30 points)
    weather_score = calculate_weather_score([top, bottom, footwear], user_preferences["weather"])
    score += weather_score * 30
    
    # Occasion appropriateness (0-25 points)
    occasion_score = calculate_occasion_score([top, bottom, footwear], user_preferences["occasion"])
    score += occasion_score * 25
    
    # Color compatibility (0-20 points)
    color_score = calculate_color_compatibility(top, bottom, footwear)
    score += color_score * 20
    
    # Pattern compatibility (0-15 points)
    pattern_score = calculate_pattern_compatibility(top, bottom, footwear)
    score += pattern_score * 15
    
    # Style consistency (0-10 points)
    style_score = calculate_style_consistency(top, bottom, footwear)
    score += style_score * 10
    
    return score

def calculate_weather_score(items, weather):
    weather_to_season = {
        "hot": "summer",
        "warm": "spring",
        "cool": "fall",
        "cold": "winter",
        "rainy": "fall"  
    }
    
    target_season = weather_to_season.get(weather, weather)
    
    # Calculate percentage of items appropriate for the weather
    matches = sum(1 for item in items if item.season == target_season)
    return matches / len(items)

def calculate_occasion_score(items, occasion):
    compatible_occasions = {
        "casual": ["casual", "lounge", "outdoor"],
        "work": ["work", "formal", "special_event"],
        "formal": ["formal", "work", "special_event"],
        "athletic": ["athletic", "outdoor"],
        "outdoor": ["outdoor", "athletic", "casual"],
        "lounge": ["lounge", "casual"],
        "party": ["party", "casual", "special_event"],
        "special_event": ["special_event", "formal", "party"]
    }
    
    target_occasions = compatible_occasions.get(occasion, [occasion])
    
    # Calculate percentage of items appropriate for the occasion
    matches = sum(1 for item in items if item.occasion in target_occasions)
    return matches / len(items)

def calculate_color_compatibility(top, bottom, footwear):
    # Get colors from each item
    top_color = top.color.lower()
    bottom_color = bottom.color.lower()
    footwear_color = footwear.color.lower()

    # Calculate pairwise compatibility scores
    top_bottom_score = color_pair_compatibility(top_color, bottom_color)
    bottom_footwear_score = color_pair_compatibility(bottom_color, footwear_color)
    top_footwear_score = color_pair_compatibility(top_color, footwear_color)

    # Weight the scores (top-bottom pairing is most important)
    weighted_score = (0.5 * top_bottom_score) + (0.25 * bottom_footwear_score) + (0.25 * top_footwear_score)

    return weighted_score

def color_pair_compatibility(color1, color2):
    # Handle missing or None values
    if not color1 or not color2:
        return 0.5 # Default moderate score
    
    # Check for same color (monochromatic)
    if color1 == color2:
        return 0.9 # High score for matching colors
    
    # Check for neutral colors (They go well with everything)
    neutrals = ["black", "white", "gray", "beige", "navy"]
    if color1 in neutrals or color2 in neutrals:
        return 0.85 # Good score for neutrals
    
    # Check for bad combinations 
    if is_bad_color_combination(color1, color2):
        return 0.2 # Low score for clashing colors
    
    # Default to decent compatibility if not specially bad
    return 0.7

def is_bad_color_combination(color1, color2):

    # Define clashing color pairs (based on high-contrast & unbalanced hues)
    clashing_pairs = {
        ("red", "green"), 
        ("orange", "blue"), 
        ("yellow", "purple"), 
        ("red", "pink"), 
        ("red", "orange"), 
        ("green", "purple"), 
        ("blue", "brown"), 
        ("yellow", "gray"), 
        ("purple", "brown")
    }

    # Ensure colors are in lowercase for consistency 
    color1, color2 = color1.lower(), color2.lower()

    # Check if colors are in the clashing pair set (both directions)
    if (color1, color2) in clashing_pairs or (color2, color1) in clashing_pairs:
        return True
    
    return False

def calculate_pattern_compatibility(top, bottom, footwear):
    patterns = [top.pattern, bottom.pattern, footwear.pattern]

    # Handle missing pattern data
    patterns = [p.lower() if p else "solid" for p in patterns]

    # Define pattern categories
    statement_patterns = ["floral", "animal", "graphic", "abstract", "camouflage", "tie-dye"]
    structured_patterns = ["striped", "plaid", "checkered", "geometric"]
    subtle_patterns = ["polka dot", "solid"]

    # Count patterns by category 
    statement_count = sum(1 for p in patterns if p in statement_patterns)
    structured_count = sum(1 for p in patterns if p in structured_patterns)

    # Rule 1: Only one statement pattern
    if statement_count > 1:
        return 0.3  # Multiple statement patterns clash
    
    # Rule 2: All solid is safe but boring
    if patterns.count("solid") == 3:
        return 0.8
    
    # Rule 3: Two structured patterns usually clash
    if structured_count > 1:
        return 0.5
    
    # Rule 4: One statement or structured + solids is good
    if (statement_count == 1 or structured_count == 1) and patterns.count("solid") >= 1:
        return 0.9
    
    # Default moderate score
    return 0.6


#FIXME
def calculate_style_consistency(top, bottom, footwear):
    pass

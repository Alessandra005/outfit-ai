import os
import certifi
import torch
import clip
from PIL import Image 

def classify(image_path):
    
    # Set the SSL certificate path
    os.environ['SSL_CERT_FILE'] = certifi.where()

    # Load the model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device = device)

    # Load and preprocess the image
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

    # Encode image
    with torch.no_grad():
        image_features = model.encode_image(image)

    # Define main category (Top, bottom, footwear)
    main_categories = ["top", "bottom", "footwear"]

    # Compute similarity with main categories
    main_category = compute_similarity(main_categories, image_features, model, device)

    # Define subcategories 
    if main_category == "top":
        sub_categories = ["t-shirt",
        "button-up shirt",
        "blouse",
        "polo shirt",
        "tank top",
        "sweater",
        "sweatshirt",
        "cardigan",
        "turtleneck",
        "crop top",
        "tunic",
        "athletic top",
        "henley",
        "flannel shirt",
        "printed shirt",
        "jacket"]

    elif main_category == "bottom":
        sub_categories = ["jeans",
        "slacks",
        "chinos",
        "shorts",
        "skirt",
        "leggings",
        "sweatpants",
        "cargo pants",
        "athletic shorts",
        "bermuda shorts",
        "culottes",
        "capri pants",
        "palazzo pants",
        "cargo shorts",
        "denim shorts"]

    elif main_category == "footwear":
        sub_categories = ["sneakers",
        "dress shoes",
        "loafers",
        "boots",
        "sandals",
        "heels",
        "flats",
        "slip-ons",
        "ankle boots",
        "running shoes",
        "hiking shoes",
        "mules",
        "espadrilles",
        "boat shoes",
        "flip-flops"]

    # Compute similarity with sub-categories
    sub_category = compute_similarity(sub_categories, image_features, model, device)

    # Define colors
    colors = ["red", "blue", "black", "white", "green", "yellow"]

    # Compute similarity with colors
    color = compute_similarity(colors, image_features, model, device)

    # Define seasonal setting
    seasons = ["spring", "summer", "fall", "winter"]

    # Compute similarity with seasonal setting
    season = compute_similarity(seasons, image_features, model, device)

    prediction = [main_category, sub_category, color, season]

    return prediction

def compute_similarity(categories, image_features, model, device):

    # Tokenize categories
    text_inputs = clip.tokenize(categories).to(device)

    # Encode
    with torch.no_grad():
        text_features = model.encode_text(text_inputs)

    # Compute similiraty 
    text_features /= text_features.norm(dim=1, keepdim=True)
    similarity = (image_features @ text_features.T).squeeze(0) # Compute cosine similarity

    # Get the best match 
    best_match = similarity.argmax().item()

    return categories[best_match]


print(classify("/Users/eduardogoncalvez/Desktop/jacket.jpg"))
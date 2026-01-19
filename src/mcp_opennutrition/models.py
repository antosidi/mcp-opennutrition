"""Pydantic models for OpenNutrition food data."""

from typing import List, Optional
from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    """Reference to an external food database source."""

    id: str | int = Field(description="Source database identifier")
    reference: str = Field(description="Type of reference (e.g., 'FDC ID', 'Food ID')")
    database: str = Field(description="Name of the source database")
    name: str = Field(description="Food name in the source database")
    url: str = Field(description="URL to the source entry")


class ServingSize(BaseModel):
    """Serving size information."""

    unit: str = Field(description="Unit of measurement (e.g., 'g', 'oz', 'ml')")
    quantity: float = Field(description="Quantity in the specified unit")


class Serving(BaseModel):
    """Common and metric serving sizes."""

    common: Optional[ServingSize] = Field(
        None, description="Common serving size (e.g., cups, pieces)"
    )
    metric: Optional[ServingSize] = Field(
        None, description="Metric serving size (grams, ml)"
    )


class PackageSize(BaseModel):
    """Package size information for packaged foods."""

    unit: Optional[str] = Field(None, description="Unit of measurement")
    quantity: Optional[float] = Field(None, description="Quantity in the package")


class Nutrition100g(BaseModel):
    """Nutritional information per 100 grams."""

    # Macronutrients
    calories: Optional[float] = Field(None, description="Energy in kcal")
    protein: Optional[float] = Field(None, description="Protein in grams")
    total_fat: Optional[float] = Field(None, description="Total fat in grams")
    carbohydrates: Optional[float] = Field(None, description="Total carbohydrates in grams")
    dietary_fiber: Optional[float] = Field(None, description="Dietary fiber in grams")
    total_sugars: Optional[float] = Field(None, description="Total sugars in grams")
    added_sugars: Optional[float] = Field(None, description="Added sugars in grams")

    # Fat breakdown
    saturated_fats: Optional[float] = Field(None, description="Saturated fats in grams")
    monounsaturated_fats: Optional[float] = Field(
        None, description="Monounsaturated fats in grams"
    )
    polyunsaturated_fats: Optional[float] = Field(
        None, description="Polyunsaturated fats in grams"
    )
    trans_fats: Optional[float] = Field(None, description="Trans fats in grams")
    cholesterol: Optional[float] = Field(None, description="Cholesterol in mg")

    # Omega fatty acids
    omega_3: Optional[float] = Field(None, description="Omega-3 fatty acids in grams")
    omega_6: Optional[float] = Field(None, description="Omega-6 fatty acids in grams")
    omega_9: Optional[float] = Field(None, description="Omega-9 fatty acids in grams")

    # Minerals
    sodium: Optional[float] = Field(None, description="Sodium in mg")
    potassium: Optional[float] = Field(None, description="Potassium in mg")
    calcium: Optional[float] = Field(None, description="Calcium in mg")
    iron: Optional[float] = Field(None, description="Iron in mg")
    magnesium: Optional[float] = Field(None, description="Magnesium in mg")
    phosphorus: Optional[float] = Field(None, description="Phosphorus in mg")
    zinc: Optional[float] = Field(None, description="Zinc in mg")
    copper: Optional[float] = Field(None, description="Copper in mg")
    manganese: Optional[float] = Field(None, description="Manganese in mg")
    selenium: Optional[float] = Field(None, description="Selenium in mcg")
    chromium: Optional[float] = Field(None, description="Chromium in mcg")
    molybdenum: Optional[float] = Field(None, description="Molybdenum in mcg")
    iodine: Optional[float] = Field(None, description="Iodine in mcg")
    chlorine: Optional[float] = Field(None, description="Chlorine in mg")

    # Vitamins
    vitamin_a: Optional[float] = Field(None, description="Vitamin A in mcg RAE")
    vitamin_c: Optional[float] = Field(None, description="Vitamin C in mg")
    vitamin_d: Optional[float] = Field(None, description="Vitamin D in mcg")
    vitamin_e: Optional[float] = Field(None, description="Vitamin E in mg")
    vitamin_k: Optional[float] = Field(None, description="Vitamin K in mcg")
    thiamin: Optional[float] = Field(None, description="Thiamin (B1) in mg")
    riboflavin: Optional[float] = Field(None, description="Riboflavin (B2) in mg")
    niacin: Optional[float] = Field(None, description="Niacin (B3) in mg")
    vitamin_b6: Optional[float] = Field(None, description="Vitamin B6 in mg")
    vitamin_b12: Optional[float] = Field(None, description="Vitamin B12 in mcg")
    folate_dfe: Optional[float] = Field(None, description="Folate in mcg DFE")
    pantothenic_acid: Optional[float] = Field(
        None, description="Pantothenic acid (B5) in mg"
    )
    biotin: Optional[float] = Field(None, description="Biotin in mcg")
    choline: Optional[float] = Field(None, description="Choline in mg")

    # Amino acids
    tryptophan: Optional[float] = Field(None, description="Tryptophan in grams")
    threonine: Optional[float] = Field(None, description="Threonine in grams")
    isoleucine: Optional[float] = Field(None, description="Isoleucine in grams")
    leucine: Optional[float] = Field(None, description="Leucine in grams")
    lysine: Optional[float] = Field(None, description="Lysine in grams")
    methionine: Optional[float] = Field(None, description="Methionine in grams")
    cystine: Optional[float] = Field(None, description="Cystine in grams")
    phenylalanine: Optional[float] = Field(None, description="Phenylalanine in grams")
    tyrosine: Optional[float] = Field(None, description="Tyrosine in grams")
    valine: Optional[float] = Field(None, description="Valine in grams")
    arginine: Optional[float] = Field(None, description="Arginine in grams")
    histidine: Optional[float] = Field(None, description="Histidine in grams")
    alanine: Optional[float] = Field(None, description="Alanine in grams")
    aspartic_acid: Optional[float] = Field(None, description="Aspartic acid in grams")
    glutamic_acid: Optional[float] = Field(None, description="Glutamic acid in grams")
    glycine: Optional[float] = Field(None, description="Glycine in grams")
    proline: Optional[float] = Field(None, description="Proline in grams")
    serine: Optional[float] = Field(None, description="Serine in grams")

    # Other
    water: Optional[float] = Field(None, description="Water content in grams")
    caffeine: Optional[float] = Field(None, description="Caffeine in mg")
    ethyl_alcohol: Optional[float] = Field(None, description="Alcohol content in grams")

    class Config:
        extra = "allow"


class IngredientAnalysis(BaseModel):
    """Analysis of food ingredients."""

    vegetarian: Optional[bool] = Field(None, description="Whether the food is vegetarian")
    vegan: Optional[bool] = Field(None, description="Whether the food is vegan")
    palm_oil_free: Optional[bool] = Field(
        None, description="Whether the food is palm oil free"
    )

    class Config:
        extra = "allow"


class FoodItem(BaseModel):
    """A food item from the OpenNutrition database."""

    id: str = Field(description="Unique food identifier (starts with 'fd_')")
    name: str = Field(description="Common name of the food")
    type: str = Field(description="Food type (e.g., 'everyday', 'branded')")
    ean_13: str = Field(default="", description="EAN-13 barcode if available")
    labels: Optional[List[str]] = Field(
        None, description="Labels/tags for the food (e.g., 'cooked', 'organic')"
    )
    nutrition_100g: Optional[Nutrition100g] = Field(
        None, description="Nutritional information per 100 grams"
    )
    alternate_names: Optional[List[str]] = Field(
        None, description="Alternative names or synonyms for the food"
    )
    source: Optional[List[SourceReference]] = Field(
        None, description="References to external food databases"
    )
    serving: Optional[Serving] = Field(None, description="Serving size information")
    package_size: Optional[PackageSize] = Field(
        None, description="Package size for packaged foods"
    )
    ingredient_analysis: Optional[IngredientAnalysis] = Field(
        None, description="Analysis of ingredients (vegan, vegetarian, etc.)"
    )

    class Config:
        extra = "allow"

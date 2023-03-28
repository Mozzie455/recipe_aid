from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from .constant.http_status_code import HTTP_200_OK, HTTP_204_NO_CONTENT
from .constant.http_status_code import HTTP_201_CREATED
from .constant.http_status_code import HTTP_202_ACCEPTED
from .constant.http_status_code import HTTP_404_NOT_FOUND
from .constant.http_status_code import HTTP_409_CONFLICT
from src.models import db
from .models import Recipe


main = Blueprint('main', __name__, url_prefix="/api/v1/recipe")


@main.route('/recipes', methods=['GET'])
def get_recipes():
    data = []
    recipes = Recipe.query.filter_by().paginate(page=1, per_page=5)
    for recipe in recipes:
        data.append({
            'recipe_id': recipe.recipe_id,
            'recipe_name': recipe.recipe_name,
            'serving_size': recipe.serving_size,
            'cooking_time': recipe.cooking_time,
            'ingredients': recipe.ingredients,
            'instructions': recipe.instructions
        })

        meta = {
            "page": recipes.page,
            'pages': recipes.pages,
            'total_count': recipes.total,
            'prev_page': recipes.prev_num,
            'next_page': recipes.next_num,
            'has_next': recipes.has_next,
            'has_prev': recipes.has_prev,

        }

        return jsonify({'data': data, 'meta': meta}), HTTP_200_OK

    return jsonify(
        {"message": "Recipe does not exist"}), HTTP_404_NOT_FOUND


@main.route('/recipe_details/<string:recipe_name>', methods=["GET"])
def recipe_details(recipe_name: str):
    """Returns HTTP_200_OK status if the recipe exists """
    recipe = Recipe.query.filter_by(recipe_name=recipe_name).first()
    if recipe:
        return jsonify(
            {
                'recipe_name': recipe.recipe_name,
                'serving_size': recipe.serving_size,
                'cooking_time': recipe.cooking_time,
                'ingredients': recipe.ingredients,
                'instructions': recipe.instructions
            }), HTTP_200_OK
    else:
        return jsonify(
            message="That recipe does not exist"), HTTP_404_NOT_FOUND


@main.route('/add_recipe', methods=['POST'])
@jwt_required()
def add_recipe():

    recipe_name = request.json["recipe_name"]
    test = Recipe.query.filter_by(recipe_name=recipe_name,).first()
    if test:
        return jsonify(
            message="There is already a recipe by that name"
        ), HTTP_409_CONFLICT
    else:
        serving_size = request.json["serving_size"]
        cooking_time = request.json["cooking_time"]
        ingredients = request.json["ingredients"]
        instructions = request.json["instructions"]

        new_recipe = Recipe(recipe_name=recipe_name,
                            serving_size=serving_size,
                            cooking_time=cooking_time,
                            ingredients=ingredients,
                            instructions=instructions
                            )

        db.session.add(new_recipe)
        db.session.commit()
        return jsonify(message="You added a recipe"), HTTP_201_CREATED


@main.route('/edit_recipe/<int:recipe_id>', methods=['PUT'])
@jwt_required()
def edit_recipe(recipe_id: int):
    recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
    if recipe is None:
        return jsonify(
            {"message": "That recipe does not exist"}), HTTP_404_NOT_FOUND
    if recipe:
        recipe.recipe_name = request.json["recipe_name"]
        recipe.serving_size = request.json["serving_size"]
        recipe.cooking_time = request.json["cooking_time"]
        recipe.ingredients = request.json["ingredients"]
        recipe.instructions = request.json["instructions"]
        db.session.commit()

    return jsonify(
        {'recipe_name': recipe.recipe_name,
         'serving_size': recipe.serving_size,
         'cooking_time': recipe.cooking_time,
         'ingredients': recipe.ingredients,
         'instructions': recipe.instructions}), HTTP_202_ACCEPTED


@main.route('/remove_recipe/<string:recipe_name>', methods=['DELETE'])
@jwt_required()
def remove_recipe(recipe_name: str):
    recipe_name = request.json["recipe_name"]
    recipe = Recipe.query.filter_by(recipe_name=recipe_name).first()
    if not recipe:
        return jsonify(message="Recipe not found"), HTTP_404_NOT_FOUND

    db.session.delete(recipe)
    db.session.commit()
    return jsonify({}), HTTP_204_NO_CONTENT

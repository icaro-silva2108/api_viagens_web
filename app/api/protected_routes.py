from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.services import user_service, reservation_service, utilities, security
from app.api.auth import get_access_token_identity, get_refresh_id, send_access_token

protected_routes = Blueprint("protected_routes", __name__)

@protected_routes.route("/profile", methods=["GET"])
@jwt_required()
def myprofile():

    # ID usuário
    user_id = get_access_token_identity()

    # Caso erro de autorização
    if not user_id:
        return jsonify({
            "success" : False,
            "message" : "Usuário não existe ou não está autorizado"
            }), 401

    # Query de usuário
    user = utilities.search_user_by_id(user_id)

    if not user:
        return jsonify({
            "success" : False,
            "message" : "Usuário não encontrado."
            }), 404

    # Dados usuário
    name, email, birth_date = user

    return jsonify({
        "success" : True,
        "user" : {
            "id" : user_id,
            "name" : name,
            "email" : email,
            "birth_date" : birth_date
            }
        }), 200

@protected_routes.route("/reservations", methods=["POST"])
@jwt_required()
def create_reservation():

    # ID usuário
    user_id = get_access_token_identity()

    # Caso erro de autorização
    if not user_id:
        return jsonify({
            "success" : False,
            "message" : "Usuário não existe ou não está autorizado"
            }), 401

    # JSON
    data = request.get_json()
    if not data:
        return jsonify({
            "success" : False,
            "message" : "JSON inválido"
            }), 400

    # ID destino
    destination_id = data.get("destination_id")

    if not utilities.search_destination(destination_id):
        return jsonify({
            "success" : False,
            "message" : "Destino não disponível ou não encontrado."
            }), 404

    # Data da viagem
    travel_date_str = data.get("travel_date")
    travel_date, error = utilities.travel_date_validation(travel_date_str)

    if not travel_date:
        
        if error == "format":
            return jsonify({
                "success" : False,
                "message" : "Formato de data inválido (dd/mm/aaaa)."
                }), 400

        elif error == "future":
            return jsonify({
                "success" : False,
                "message" : "Data inválida. São aceitas somente datas posteriores à data de hoje."
                }), 400

    reservation_confirm = reservation_service.create_reservation(user_id, destination_id, travel_date)

    if not reservation_confirm:
        return jsonify({
            "success" : False,
            "message" : "Não foi possível criar a reserva."
        }), 500

    return jsonify({
        "success" : True,
        "reservation_id" : reservation_confirm
        }), 201

@protected_routes.route("/reservations", methods=["GET"])
@jwt_required()
def show_user_reservations():

    # ID usuário
    user_id = get_access_token_identity()

    # Caso erro de autorização
    if not user_id:
        return jsonify({
            "success" : False,
            "message" : "Usuário não existe ou não está autorizado"
            }), 401

    # Reservas do usuário
    reservations = reservation_service.show_reservations(user_id)

    if not reservations:
        return jsonify({
            "success" : True,
            "user_reservations" : []
            }), 200

    results = []

    for r in reservations:
        results.append({
            "id" : r[0],
            "city" : r[1],
            "country" : r[2],
            "travel_date" : r[3],
            "status" : r[4],
            "price" : r[5],
            "img_url" : r[6],
        })

    return jsonify({
        "success" : True,
        "user_reservations" : results
        }), 200

@protected_routes.route("/reservations/<int:res_id>", methods=["DELETE"])
@jwt_required()
def cancel_reservation(res_id):

    # ID usuário
    user_id = get_access_token_identity()

    # Caso erro de autorização
    if not user_id:
        return jsonify({
            "success" : False,
            "message" : "Usuário não existe ou não está autorizado"
            }), 401

    cancel_confirm = reservation_service.cancel_reservation(res_id, user_id)

    if not cancel_confirm:
        return jsonify({
            "success" : False,
            "message" : "Reserva não encontrada ou não pertence ao usuário."
            }), 404

    return jsonify({
        "success" : True,
        "message" : f"Reserva de ID: {res_id} cancelada com sucesso.",
        "canceled_res_id" : res_id
        }), 200

@protected_routes.route("/profile", methods=["PATCH"])
@jwt_required()
def update_profile():

    # ID usuário
    user_id = get_access_token_identity()

    # Caso erro de autorização
    if not user_id:
        return jsonify({
            "success" : False,
            "message" : "Usuário não existe ou não está autorizado"
            }), 401

    # Dados a serem atualizados
    data = request.get_json()

    if not data:
        return jsonify({
            "success" : False,
            "message" : "JSON inválido"
            }), 400

    allowed_keys = {"name", "email", "password", "password_confirm", "birth_date"}

    # Tratamento dos dados vazios ou instancias diferentes de string
    data = {
        k : v.strip()
        for k, v in data.items()
        if (
            k in allowed_keys and
            isinstance(v, str) and
            v.strip()
            )
        }

    # Tratamento de nome
    if "name" in data:

        name = data["name"].title()
        data["name"] = name

    # Tratamento de email
    if "email" in data:
    
        email = data.get("email")
        if not utilities.email_format_validation(email):
            return jsonify({
                "success" : False,
                "message" : "Formato de email inválido(email@email.com)."
                }), 400

    # Tratamento de senha
    if "password" in data:

        if "password_confirm" not in data:
            return jsonify({
                "success" : False,
                "message" : "É necessário fazer a confirmação de senha."
                }), 400

        password = data.get("password")
        password_confirm = data.get("password_confirm")

        if password != password_confirm:
            return jsonify({
                "success" : False,
                "message" : "A senha e a confirmação devem ser iguais."
                }), 400

        if len(password) < 8:
            return jsonify({
            "success" : False,
            "message" : "A senha precisa ter pelo menos 8 dígitos."
                }), 400

        data.pop("password")
        data.pop("password_confirm")

        password_hash = security.hash_password(password)
        data.update({"password_hash" : password_hash})
    
    # Tratamento de data de nascimento
    if "birth_date" in data:

        birth_date_str = data.get("birth_date")
        birth_date, error = utilities.birth_date_validation(birth_date_str)
        if not birth_date:

            if error == "format":
                return jsonify({
                    "success" : False,
                    "message" : "Formato de data inválido (dd/mm/aaaa)."
                    }), 400

            if error == "age":
                return jsonify({
                    "success" : False,
                    "message" : "A data a ser alterada deve representar pelo menos 16 anos."
                    }), 400
        
        data["birth_date"] = birth_date

    # Caso pós tratamento os dados estejam vazios
    if not data:
        return jsonify({
            "success" : False,
            "message" : "Não há dados válidos para alterar."
            }), 400

    update_confirm = user_service.change_user_info(user_id, data)
    if not update_confirm:
        return jsonify({
            "success" : False,
            "message" : "Não foi possível alterar os dados."
        }), 500

    return jsonify({
        "success" : True,
        "message" : "Dados alterados com sucesso."
        }), 200

@protected_routes.route("/profile", methods=["DELETE"])
@jwt_required(refresh=True)
def delete_user():

    # ID usuário
    user_id = get_access_token_identity()

    # Caso erro de autorização
    if not user_id:
        return jsonify({
            "success" : False,
            "message" : "Usuário não existe ou não está autorizado"
            }), 401

    # Verifica se usuário possui reservas
    user_reservations = utilities.search_user_reservation(user_id)

    # Se tiver reservas, impede o cancelamento
    if user_reservations:
        return jsonify({
            "success" : False,
            "message" : "Não é possível cancelar cadastro com reservas ativas."
            }), 400

    delete_confirm = user_service.delete_user(user_id)

    # Caso de erro ao deletar
    if not delete_confirm:
        return jsonify({
            "success" : False,
            "message" : "Não foi possível excluir o cadastro."
            }), 500

    # ID refresh token
    refresh_id = get_refresh_id()

    # Confirmação de revogação
    revoke_confirm = utilities.add_revoked_tokens(refresh_id)
    if not revoke_confirm:
        return jsonify({
            "success" : False,
            "message" : "Não foi possível revogar o Refresh Token."
            }), 500

    return jsonify({
        "success" : True,
        "message" : "Cadastro cancelado com sucesso."
        }), 200

@protected_routes.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():

    try:
        # ID usuário
        user_id = get_access_token_identity()

        # Novo access token que mantém sessão
        new_access_token = send_access_token(user_id)
        return jsonify({
            "success" : True,
            "access_token" : new_access_token
            }), 200

    except Exception as e:
        return jsonify({
            "success" : False,
            "message" : f"Erro interno: {e}"
            }), 500

@protected_routes.route("/logout", methods=["POST"])
@jwt_required(refresh=True)
def logout():

    try:

        # ID refresh token
        refresh_id = get_refresh_id()

        # Confirmação de revogação
        revoke_confirm = utilities.add_revoked_tokens(refresh_id)
        if not revoke_confirm:
            return jsonify({
                "success" : False,
                "message" : "Não foi possível revogar o Refresh Token."
                }), 500

        return jsonify({
            "success" : True,
            "message" : "Logout realizado com sucesso. Refresh Token revogado."
            }), 200

    except Exception as e:
        return jsonify({
            "success" : False,
            "message" : f"Erro interno: {e}"
            }), 500
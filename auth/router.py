from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse

from database import get_async_session
from auth.utils import create_user, verify_password, create_access_token, get_user_by_email, get_current_user
from auth.schemas import UserCreate, UserLogin, UserRead


router = APIRouter(
    tags=['Auth']
)


@router.post('/register')
async def register(
    user: UserCreate,
    session = Depends(get_async_session)
):
    '''
    Регистрация пользователя
    '''

    try:
        # Проверка пользователя на наличие регистрации
        user_in_db = await get_user_by_email(session, user.email)

        if user_in_db:
            # Ошибка, если пользователь уже зарегистрирован
            raise HTTPException(status_code=409, detail='User already registered')

        # Запись пользователя в бд
        await create_user(session, user)

        # Создание JWT токена
        jwt_token = await create_access_token(session, user.email)

        response_data = {
                'status': 'success',
                'data': {
                    'jwt_token': jwt_token,
                    'token_type': 'jwt_token'
                },
                'detail': None
            }
        response = JSONResponse(content=response_data, status_code=200)
        response.set_cookie(key='jwt_token', value=jwt_token, max_age=3600)
        print('куки добавлены')

        return response

    # Ошибка
    except HTTPException as error:
        response_data = {
            'status': 'error',
            'data': None,
            'detail': error.detail
        }
        return JSONResponse(content=response_data, status_code=error.status_code)

    # Ошибка сервера
    except Exception as error:
        response_data = {
            'status': 'error',
            'data': str(error),
            'detail': 'Server error'
        }
        print(JSONResponse(content=response_data, status_code=500))
    

@router.post('/login')
async def login(
    user: UserLogin,
    session = Depends(get_async_session)
):
    '''
    Вход в аккаунт
    '''

    try:
        # Проверка пароля пользователя
        if await verify_password(session, user.email, user.password):
            
            # Создание JWT токена
            jwt_token = await create_access_token(session, user.email)

            response_data = {
                'status': 'success',
                'data': {
                    'jwt_token': jwt_token,
                    'token_type': 'jwt_token'
                },
                'detail': None
            }
            response = JSONResponse(content=response_data, status_code=200)

            # Добавление токена в куки
            response.set_cookie(key='jwt_token', value=jwt_token, max_age=3600)
            print('куки добавлены')

            return response
        
        # Ошибка авторизации
        else:
            raise HTTPException(status_code=400, detail='Invalid credentials')

    # Ошибка
    except HTTPException as error:
        response_data = {
            'status': 'error',
            'data': None,
            'detail': error.detail
        }
        return JSONResponse(content=response_data, status_code=error.status_code)

    # Ошибка сервера
    except Exception as error:
        print(error)
        response_data = {
            'status': 'error',
            'data': str(error),
            'detail': 'Server error'
        }
        return JSONResponse(content=response_data, status_code=500)

    


@router.post('/logout')
async def logout():
    '''
    Выход из аккаунта путем удаления куки в браузере
    '''

    try:
        response_data = {
            'status': 'success',
            'data': None,
            'detail': None
        }
        response = JSONResponse(content=response_data)
        response.delete_cookie('jwt_token')

        return response

    # Ошибка сервера
    except Exception as error:
        response_data = {
            'status': 'error',
            'data': str(error),
            'detail': 'Server error'
        }
        return JSONResponse(content=response_data, status_code=500)
    

@router.get('/test-auth')
async def test_auth(
    request: Request,
    user: UserRead = Depends(get_current_user)
):
    '''
    Пример проверки на наличие пользователя
    '''

    try:
        if user is None:
            # Пользователь не авторизован
            raise HTTPException(status_code=401, detail='Unauthorized')

        response_data = {
            'status': 'success',
            'data': None,
            'detail': None
        }
        return JSONResponse(content=response_data)
    
    # Ошибка
    except HTTPException as error:
        response_data = {
            'status': 'error',
            'data': None,
            'detail': error.detail
        }
        return JSONResponse(content=response_data, status_code=error.status_code)

    # Ошибка сервера
    except Exception as error:
        response_data = {
            'status': 'error',
            'data': str(error),
            'detail': 'Server error'
        }
        return JSONResponse(content=response_data, status_code=500)

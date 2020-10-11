# 파이썬의 데코레이터
- Decorator: 장식하는 도구
    - clean code
        - syntax sugar (편리구문: 타이핑 감소 or 가독성 향상을 위해 다른 표현으로 코딩할 수 있게 해주는 기능)
        - 함수와 메서드 기능 쉽게 수정하기 위한 수단
        - 데코레이터 이후에 나오는 것을 데코레이터의 첫번째 파라미터로 하고, 데코레이터의 결과 값 반환
    - fluent python
        - 다른 함수를 인수로 받는 callable (callable: 호출할 수 있는 객체)
        - 메타프로그래밍(런타임에 프로그램 행위 변경) 편리
        - 모듈이 로딩될 때 바로 실행, import 타임에 실행

- 적용범위
    - 호출 가능 객체(함수, 메서드, 제너레이터, 클래스)에 적용
- 기능(effective python chapter 6)
    - **로그남기기**
    - **시간 측정**
    - 접근 제어와 인증 시행
    - 비율 제한
    - 캐싱 및 기타 추가기능 구현
    - 입력 인수와 반환 값을 접근하거나 수정 가능(ex: 재귀호출에서 함수 호출의 스택을 디버깅하는 경우)
        - 시맨틱 강조
        - 디버깅
        - 함수 등록
- 라이브러리
    - 표준라이브러리
        - @staticmethod
        - @classmethod
        - @property (effective python chapter 4)
    - functools
        - **wraps**
        - lru_cache (memoization, Least Recently Used)
        - ...
    - numba
        - **@jit, @njit**


```python
def original():
    pass

def modifier(func):
    pass

original = modifier(original)
```


```python
@modifier # Decorator 
def original(): # 데코레이팅된(decorated) 함수 또는 래핑(wrapped)된 객체
    pass
```

- 보고서 생성 프로그램: 
    - 비즈니스 로직 30개
    - 로직 간 단계에 입출력 로깅 추가해야 하는 경우
    - 로직함수 각각에 로깅호출 수작업 vs @audit_log

### 데코레이터: 감싸고 있는 함수를 호출하기 전/후, 추가로 코드 실행 가능

#### null_decorator


```python
def null_decorator(func):
    return func
```


```python
def greet():
    return 'hello'
    
greet = null_decorator(greet)
greet()
```




    'hello'




```python
@null_decorator
def greet():
    '''return greeting'''
    return 'hello'

greet()
```




    'hello'




```python
print(greet)
print(greet.__name__)
print(greet.__doc__)
print(null_decorator(greet))
```

    <function greet at 0x7f3f23afaae8>
    greet
    return greeting
    <function greet at 0x7f3f23afaae8>



```python
def uppercase(func):
    def wrapper():
        result = func()
        return result.upper()
    return wrapper

@uppercase
def greet():
    '''return greeting'''
    return 'hello'

greet()
```




    'HELLO'




```python
# 데코레이트된 함수 메타데이터에 접근하면, 대신 감싼 클로저(wrapper)의 메타데이터 표시
print(uppercase(greet))
print(uppercase(greet).__name__)
print(uppercase(greet).__doc__)
```

    <function uppercase.<locals>.wrapper at 0x7f3f23afa620>
    wrapper
    None



```python
help(greet)
```

    Help on function wrapper in module __main__:
    
    wrapper()
    


- uppercase 함수는 그 안에 정의된 wrapper 반환
- 데코레이터를 호출한 후 wrapper 함수가 greet 이름에 할당
- 디버깅시 문제 발생
- 해결책
    - 디버깅 가능한 데코레이터 작성
    - functools의 wraps 헬퍼 함수 사용

#### wraps: 입력 함수의 docstring, metadata 전달


```python
from functools import wraps

def uppercase(func):
    @wraps(func)
    def wrapper():
        result = func()
        return result.upper()
    return wrapper

@uppercase
def greet():
    '''return greeting'''
    return 'hello'

greet()
```




    'HELLO'




```python
print(uppercase(greet))
print(uppercase(greet).__name__)
print(uppercase(greet).__doc__)
```

    <function greet at 0x7f3f23afaea0>
    greet
    return greeting



```python
help(greet)
```

    Help on function greet in module __main__:
    
    greet()
        return greeting
    


#### trace


```python
def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f'{func.__name__}(args: {args}, kwargs: {kwargs}) -> result: {result}')
        return result
    return wrapper
        
@trace # fibonacci = trace(fibonacci)
def fibonacci(n):
    '''return the n-th fibonacci number'''
    if n in (0, 1):
        return n
    return (fibonacci(n-2) + fibonacci(n-1))

fibonacci(3)
pass
```

    fibonacci(args: (1,), kwargs: {}) -> result: 1
    fibonacci(args: (0,), kwargs: {}) -> result: 0
    fibonacci(args: (1,), kwargs: {}) -> result: 1
    fibonacci(args: (2,), kwargs: {}) -> result: 1
    fibonacci(args: (3,), kwargs: {}) -> result: 2


#### 함수 실행 시간 측정


```python
import time

def clock(func):
    @wraps(func)
    def clocked(*args):
        t0 = time.perf_counter()
        result = func(*args)
        elapsed = time.perf_counter() - t0
        name = func.__name__
        arg_str = ', '.join(repr(arg) for arg in args)
        print(f'{elapsed:.8f} {name}({arg_str}) -> {result}')
        return result
    return clocked

@clock
def snooze(seconds):
    time.sleep(seconds)
    
@clock
def factorial(n):
    return 1 if n < 2 else n*factorial(n-1)

    
print(snooze(.123))
print(f'3! = {factorial(3)}')
```

    0.12350932 snooze(0.123) -> None
    None
    0.00000124 factorial(1) -> 1
    0.00006402 factorial(2) -> 2
    0.00010787 factorial(3) -> 6
    3! = 6


#### numba, jit


```python
def mandel(x, y, max_iters):
    """
    Given the real and imaginary parts of a complex number,
    determine if it is a candidate for membership in the Mandelbrot
    set given a fixed number of iterations.
    """
    i = 0
    c = complex(x,y)
    z = 0.0j
    for i in range(max_iters):
        z = z*z + c
        if (z.real*z.real + z.imag*z.imag) >= 4:
            return i

    return 255

def create_fractal(min_x, max_x, min_y, max_y, image, iters):
    height = image.shape[0]
    width = image.shape[1]

    pixel_size_x = (max_x - min_x) / width
    pixel_size_y = (max_y - min_y) / height
    for x in range(width):
        real = min_x + x * pixel_size_x
        for y in range(height):
            imag = min_y + y * pixel_size_y
            color = mandel(real, imag, iters)
            image[y, x] = color

    return image

image = np.zeros((500 * 2, 750 * 2), dtype=np.uint8)
s = timer()
create_fractal(-2.0, 1.0, -1.0, 1.0, image, 20)
e = timer()
print(f'{(e - s):.3f} sec')
imshow(image)
show()
```

    4.326 sec



![png](output_23_1.png)



```python
from numba import jit

@jit
def mandel(x, y, max_iters):
    """
    Given the real and imaginary parts of a complex number,
    determine if it is a candidate for membership in the Mandelbrot
    set given a fixed number of iterations.
    """
    i = 0
    c = complex(x,y)
    z = 0.0j
    for i in range(max_iters):
        z = z*z + c
        if (z.real*z.real + z.imag*z.imag) >= 4:
            return i

    return 255

@jit
def create_fractal(min_x, max_x, min_y, max_y, image, iters):
    height = image.shape[0]
    width = image.shape[1]

    pixel_size_x = (max_x - min_x) / width
    pixel_size_y = (max_y - min_y) / height
    for x in range(width):
        real = min_x + x * pixel_size_x
        for y in range(height):
            imag = min_y + y * pixel_size_y
            color = mandel(real, imag, iters)
            image[y, x] = color

    return image

image = np.zeros((500 * 2, 750 * 2), dtype=np.uint8)
s = timer()
create_fractal(-2.0, 1.0, -1.0, 1.0, image, 20)
e = timer()
print(f'{(e - s):.3f} sec')
imshow(image)
show()
```

    0.328 sec



![png](output_24_1.png)


#### 다중 데코레이터


```python
def strong(func):
    def wrapper():
        return '<strong>' + func() + '</strong>'
    return wrapper

def emphasis(func):
    def wrapper():
        return '<em>' + func() + '</em>'
    return wrapper

@strong
@emphasis
def greet():
    return 'Hello!'

greet()
```




    '<strong><em>Hello!</em></strong>'




```python
def greet():
    return 'Hello!'

decorated_greet = strong(emphasis(greet))
decorated_greet()
```




    '<strong><em>Hello!</em></strong>'



- 파이썬 함수: 일급 객체(first-class object)
    - 변수에 할당
            bark = yell
    - 데이터 구조에 저장
            funcs = [bark, str.lower]
    - 인자로 다른 함수에 전달 
            def greet(func):
                print(func('hi'))
    - 다른 함수의 값에서 반환
            def speak(text):
                def whisper(t):
                    return t.lower() + '...'
                return whisper(text)
    - 클로저

#### 클로저: 함수를 정의할 때 존재하던 자유 변수에 대한 바인딩을 유지하는 함수
- '비전역' 외부 변수를 다루는 경우는 그 함수가 다른 함수 안에 정의된 경우 한정


```python
# 변수범위

b = 6
def f(a):
    print(a)
    print(b)
    b = 9

f(3)
```

    3



    ---------------------------------------------------------------------------

    UnboundLocalError                         Traceback (most recent call last)

    <ipython-input-162-bceea8621c1b> in <module>
          7     b = 9
          8 
    ----> 9 f(3)
    

    <ipython-input-162-bceea8621c1b> in f(a)
          4 def f(a):
          5     print(a)
    ----> 6     print(b)
          7     b = 9
          8 


    UnboundLocalError: local variable 'b' referenced before assignment



```python
def make_averager():
    series = []
    
    def averager(new_value):
        series.append(new_value)
        total = sum(series)
        return total/len(series)
    return averager

avg = make_averager()
print(avg(10))
print(avg(11))
print(avg(12))
```

    10.0
    10.5
    11.0


## 함수 데코레이터
- 기능
    - 파라미터의 유효성 검사
    - 사전조건 검사
    - 기능 전체 재정의
    - 서명 변경
    - 원래 함수 결과 캐싱

## 클래스 데코레이터

- 코드재사용, DRY (Don't Repeat Yourself) 원칙 이점 공유
    - 여러 클래스에 특정 인터페이스나 기준 강제
    - 여러 클래스에 적용할 검사를 데코레이터 한 번만 시행
- 작고 간단한 클래스를 생성하고, 데코레이터로 기능 보강 (선지원 후고민?)
- 유지보수시 기존 로직 쉽게 변경

## 다른 유형의 데코레이터
- 스택 형태
- 코루틴으로 사용되는 제너레이터 (clean code 7장에서...)

## 데코레이터에 인자 전달

### 중첩함수의 데코레이터
- 고차함수(higher-order function): 함수를 파라미터로 받아서 함수를 반환하는 함수

### 데코레이터 객체
- 클래스를 사용하여 데코레이터 정의
        __init__ : 파라미터 전달
        __call__ : 데코레이터 로직 구현

## 데코레이터 활용 우수 사례
- 파라미터 변환
- 코드 추적(trace): 파라미터, 함수 실행 로깅
    - 실제 함수의 실행 경로 추적(ex: 실행 함수 로깅)
    - 함수 지표 모니터링
    - 함수의 실행 시간 측정
    - 언제 함수가 실행되고 전달된 파라미터는 무엇인지 로깅
- 파라미터 유효성 검사
- 재시도 로직 구현
- 반복작업을 데코레이터로 이동하여 클래스 단순화

## 데코레이터의 활용 - 흔한 실수 피하기

### 래핑된 원본 객체의 데이터 보존
- wraps
        __qualname__ (python 3.3)
          순수 함수명과 클래스 이름 구분

        ex: A클래스 b함수
        __name__: b
        --qualname__: A.b

### 데코레이터 부작용 처리
- 데코레이터 부작용의 잘못된 처리

- 데코레이터 부작용의 활용

### 어느곳에서나 동작하는 데코레이터 만들기

## 데코레이터와 DRY 원칙
- 처음부터 데코레이터를 만들지 않는다. 패턴이 생기고 데코레이터에 대한 추상화가 명확해지면 리팩토링 진행
- 데코레이터가 적어도 3회 이상 필요한 경우에만 구현
- 데코레이터 코드를 최소한으로 유지

## 데코레이터와 관심사의 분리
    def trace_function(function):
        ...
    @trace_function
    def operation():
        ...


    def log_execution(function):
        ...
    def measure_time(function):
        ...
    @measure_time
    @log_execution
    def operation():
        ...

## 좋은 데코레이터 분석
- 캡슐화와 관심사의 분리: 실제로 하는 일과 데코레이팅하는 일의 책임을 명확히 구분
        # Celery
        @app.task
        def mytask():
            ...

        # 웹 프레임 워크
        @route('/', method = ['GET']
        def view_handler(request):
            ...
- 독립성: 데코레이터와 데코레이팅 되는 객체는 최대한 분리
- 재사용성: 데코레이터는 여러 유형에 적용 가능한 충분히 범용적인 형태가 바람직

## 요약
- 데코레이터는 런타임에 한 함수로 다른 함수를 수정할 수 있게 해주는 문법
- 감싸고 있는 함수를 호출하기 전/후 추가로 코드 실행 가능
- 데코레이터를 사용하면 디버거와 같이 객체 내부를 조사하는 도구가 이상하게 동작 -> 내장 모듈 functool의 wraps 데코레이터 사용

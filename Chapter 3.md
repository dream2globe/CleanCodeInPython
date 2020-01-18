# Chapter 3 좋은 코드의 일반적인 특징

## General Traits of Good Code

### 목표:

- 견고한 SW의 개념을 이해
- 작업 중 잘못된 데이터를 다루는 법
- 새로운 요구 사항을 쉽게 받아들이고 확장할 수 잇는 유지보수가 쉬운 SW 설계
- 재사용 가능한 SW설계
- 개발팀의 생산성을 높이는 효율적인 코드 작성

## 1. 계약에 의한 디자인(Design by Contract)

계약에 의한 디자인이란, 관계자가 기대하는 바를 암묵적으로 코드에 삽입하는 대신 양측이 동의하는 계약을 먼저 한 다음, 계약을 어겼을 경우는 명시적으로 왜 계속할 수 없는지 예외를 발생시키는 것을 의미하며 구체적으로는 SW 컴포넌트간의 통신 중에 반드시 지켜져야 할 몇 가지 규칙을 강제하는 것을 말한다(i.e. input : int only -> output : str only)

계약은 주로 사전/사후조건을 명시하지만 때때로 불변식(함수가 실행되는 동안 일정하게 유지되는 것. 로직 확인용. doc-string에 언급)과 부작용(코드 부작용을 doc-string에 언급)을 기술함.

---

- 사전조건 : 코드 실행전에 체크/처리해야 하는 것.i.e 데이터 유효성 검사.
    - 함수나 메서드가 정상 동작하기 위해 보장해야 하는 조건을 의미함. (i.e. 초기화된 객체, null 아닌 값등) —> Type checking 보다는 유효성 검사에 가까움.
    - 계약에 의한 디자인(DbC)에서는 함수가 자체적으로 로직을 실행하기전에 유효성 검사를 하는것이 널리 쓰임.(demanding approach)
    - 위에 반대되는 것은 "클라이언트가 함수를 호출하기 전에 모든 유효성 검사를 하는 것"임(tolerant approach)
- 사후조건 : 함수 return값의 유효성 검사, 호출자가 기대하는 바를 return 받았는지 검사.
- 파이썬스러운 계약 : PEP-316 in Deferred status
    - ***(저자) 디자인시 RuntimeError, ValueError등의 예외를 발생시키는 제어 매커니즘을 추가하는것이 바람직 함. 문제를 특정하기 어려울 경우, 사용자 정의 예외를 만드는 것이 바람직.***
    - ***(저자) 데코레이터등을 사용하여 사전/사후검사 부분과 핵심 기능 부분의 코드를 격리된 상태로 유지하는 것이 바람직 함.***
- 계약에 의한 디자인(DbC) - 결론 : 이 디자인 규칙을 따름으로써...
    1. 문제가 있는 부분을 효과적으로 식별할 수 있다.
    2. 코드가 더욱 견고해 진다.
    3. 프로그램의 구조를 명확히 하는데에도 도움이 된다.
    4. 계약 작성에 대한 추가작업이 발생하며 단위 테스트를 상황에 따라 추가해야 할 수도 있다.
    - ***(저자) 이 방법을 더욱 효과적으로 하기 위해서는 무엇을 검증할 것인지 신중히 검토해야 함. Mypy와 같은 도구를 사용하면 쉽게 목적을 달성할 수 잇음.***

## 2. 방어적 프로그래밍(Defensive programming)

DbC는 계약에서 예외를 발생시키고 실패하는 모든 조건을 기술하는 대신, 방어적 프로그래밍은 객체, 함수 또는 메서드와 같은 코드의 부분을 유효하지 않은 것으로부터 보호한다는 점에서 그 접근 방식이 다르다. 방어적 프로그래밍은 특히 다른 디자인 원칙과 결합할 경우 유용하다.

### Error handling

- 설명 : 예상할 수 있는 시나리오의 오류를 처리하는 방법
- 주 목적 : 예상되는 에러에 대해서 실행이 계속 가능한지 또는 불가능 하여 프로그램을 중단할 것인지 결정하는 것.
- 적용 상황 : 일반적으로 데이터 입력 확인 시 자주 사용됨.
- 에러 처리방법
    - 값 대체: 기본값 또는 잘 알려진 상수, 초기값으로 결측값/결과값을 대체. 단, 오류 자체를 숨길 수 있으므로 매우 신중해야 함.
    - 예외 처리:예외적인 상황을 알려주고 원래의 비즈니스 로직 흐름을 유지. 단,  예외처리를 비즈니스 로직의 일부로 사용하지 말고 호출자가 알아야만 하는 실질적인 문제 발생에 대해서 사용해야 함.
    - 파이썬 예외처리 권장사항
        - 올바른 수준의 추상화 단계에서 예외처리 : 예외는 오직 한가지 일을 하는 함수의 한부분이어야 하며, 함수가 처리하는 예외는 캡슐화된 로직과 일치해야 함.

            class DataTransport:
                """다른 레벨에서 예외를 처리하는 예"""
            
               ...
            
                def deliver_event(self, event):
                    try:
                        self.connect()
                        data = event.decode()
                        self.send(data)
            
                    # 관계가 없는 두 유형의 오류.
            
            			  # connect 메서드 내에서 처리되어야 함.
            				# 만약 재시도 지원 시, 여기서 처리 가능
                    except ConnectionError as e: 
                        logger.info("connection error detected: %s", e)
                        raise
            
            			  # event.decode 메서드에 속한 에러.
                    except ValueError as e:
                        logger.error("%r contains incorrect data: %s", event, e)
                        raise
            
                def connect(self):
                    for _ in range(self.retry_n_times):
                        try:
                            self.connection = self._connector.connect()
                        except ConnectionError as e:
                            logger.info(
                                "%s: attempting new connection in %is",
                                e,
                                self.retry_threshold,
                            )
                            time.sleep(self.retry_threshold)
                        else:
                            return self.connection
                    raise ConnectionError(
                        f"Couldn't connect after {self.retry_n_times} times"
                    )
            
                def send(self, data):
                    return self.connection.send(data)

            ...
            
            def connect_with_retry(connector, retry_n_times, retry_threshold=5):
                for _ in range(retry_n_times):
                    try:
                        return connector.connect()
                    except ConnectionError as e:
                        logger.info(
                            "%s: attempting new connection in %is", e, retry_threshold
                        )
                        time.sleep(retry_threshold)
            
                # ConnectionError를 따로 분리함
                exc = ConnectionError(f"Couldn't connect after {retry_n_times} times")
                logger.exception(exc)
                raise exc
            
            
            class DataTransport:
                retry_threshold: int = 5
                retry_n_times: int = 3
            
                def __init__(self, connector):
                    self._connector = connector
                    self.connection = None
            
                def deliver_event(self, event):
                    self.connection = connect_with_retry(
                        self._connector, self.retry_n_times, self.retry_threshold
                    )
                    self.send(event)
            
                def send(self, event):
                    try:
                        return self.connection.send(event.decode())
            
                    # ValueError를 따로 분리함.
                    except ValueError as e:
                        logger.error("%r contains incorrect data: %s", event, e)
                        raise

        - Trackback 노출금지 : 파이썬의 trackback은 많은 디버깅 정보를 포함하기 때문에 역으로 악의적인 사용자에게도 유용한 정보이다. 예외가 전파되도록 할 때, 중요한 정보를 공개하지 않도록 주의해야 한다.
        - 비어있는 except 블록 지양 : 에러에 대한 지나지게 방어적인 프로그래밍은 더 큰 문제를 야기한다. 이 경우 1. 보다 구체적인 예외(i.e. AttributeError, KeyError)를 사용하거나 2. except 블록에서 실제 오류 처리를 한다.(i.e. 예외상황 로깅, 기본값 반환)

            try:
            	process_data()
            except:
            	pass

        - 원본 예외 포함: 예외의 타입을 변경할 때는 항상 raise ~ from 구문을 사용한다.

            class InternalDataError(Exception):
                """업무 도메인 데이터의 예외"""
            
            
            def process(data_dictionary, record_id):
                try:
                    return data_dictionary[record_id]
                except KeyError as e:
                    raise InternalDataError("Record not present") from e

### 파이썬에서 assertion 사용하기

- 발생하지 않아야 하는 오류를 처리하기 위해 사용하며 에러 발생시 바로 프로그램이 중단된다. 그렇기 때문에 assertion을 비즈니스 로직과 섞어나 제어 흐름 매커니즘으로 사용하지 않아야 한다.

    # assertion 사용의 안좋은 예
    try:
    	assert contition.holds(), "조건에 맞지 않음"
    except AssertionError:
      alternative_procedure()
    
    # 개선
    result = condition.holds()
    assert result > 0, "에러 {0}".format(result)

## 3. 관심사의 분리(Separation of concerns)

여기서 말하는 관심사란, 프로그램內 기능의 일부분을 의미한다. 

- SW에서 "관심사"를 분리하는 이유
    - 파급효과(코드 수정에 의한 체인리액션)를 최소화 하여 코드의 유지 보수성을 향상시키기 위함.
    - 책임(담당하고 있는 기능)에 따라 컴포넌트/계층/모듈등 적절하게 분리. 여기서 말하는 적절하게란 각 부분이 일부의 기능에 대해서만 책임을 진다는 의미.
    - (4번에서 논의)적절한 캡슐화를 통해 극복

---

### 응집력

: 객체가 작고 잘 정의된 목적을 가져야 함을 의미. 응집력이 높을 수록 좋음.

### 결합력

: 두 개 이상의 객체간의 의존성을 나타내며 서로간의 의존성/종속성이 클수록 바람직 하지 않음.

- 낮은 재사용성 : 다른 상황에서는 이 함수를 사용하기 매우 어려움.
- 파급효과 : 한 군데의 수정이 다른 부분에도 영향을 크게 미침
- 낮은 수준의 추상화 : 밀접한 두 함수는 서로 다른 추상화 레벨에서 문제를 해결하기 어렵기 때문에 관심사가 분리되어 있다고 보기 어려움.

***저자) 높은 응집력과 낮은 결합력을 갖는 것이 좋은 소프트웨어이다.***

## 4. 개발 지침 약어(Acronyms to live by)

좋은 소프트웨어 관행을 약어를 통해 쉽게 기억하자

---

### DRY/OAOO

: Do not repeat yourself, Once and only once를 의미하며 코드에 있는 지식이 단 한번, 단 한곳에 정의되어야 하고 또한 코드를 변경하려고 할때 수정이 필요한 곳이 한군데에만 있어야 한다는 SW best practice. 코드 중복은 아래와 같은 리스트를 발생시킴

- 오류가 발생하기 쉽다 : 여러번 반복된 코드가 있다면 수정과정에서 오류 발생 가능성이 높아진다.
- 비용이 비싸다. : 변경시 더 많은 시간이 들며, 팀 전체의 개발 속도를 지연시킨다.
- 신뢰성이 떨어진다. : 문맥상 여러 코드를 변경하는 경우, 사람이 모든 인스턴스의 위치를 기억해야 하며, 단일 데이터 소스가 아니므로 데이터 완결성도 저하된다.

***저자) 중복을 제거하는 방법은 간단하게는 함수 생성 기법부터 컨텍스트 관리자를 이용하거나 이터레이터, 제너레이터, 데코레이터등을 활용할 수도 있다.***

### YAGNI

: You ain't gonna need it를 의미하며 과잉 엔지니어링(굳이 필요없는 개발)을 자제하라는 의미이다. 유지보수가 가능한 소프트웨어는 미래 요구 사항을 예측하는것이 아닌 오직 현재의 요구사항을 잘 해결하기위한 소프트웨어를 수정하기 쉽게 작성하는 것이다.

### KIS

: Keep it simple을 의미하며 YAGNI와 유사하다. 문제를 올바르게 해결하는 최소한의 기능을 구현하고 필요 이상으로 솔루션을 복잡하게 만들지 않는다. 단순하게 유지하여 관리를 용이하게 한다.

### EAFP/LBYL

: Easier to ask forgiveness than permission, look before you leap를 의미한다. 전자는 일단 코드를 실행하고 실제 동작하지 않을 경우에 대항한다는 뜻이며, 후자는 사전에 미리 확인하고 실행하라는 의미이다.

***저자) 파이썬은 EAFP방식으로 이루어졌으며 그 방식을 권장한다.***

    # LBYL
    if os.path.exists(filename):
        with open(filename) as f:
            ...
            
    # EAFP        
    try:
        with open(filename) as f:
            ...
    except:
        FileNotFoundError as e:
            logger.error(e)

## 5. 컴포지션과 상속(Composition and inheritance)

OOP의 핵심개념인 상속의 장점과 단점을 알아보고 적절한 방법을 논한다. 코드 상속을 통한 코드 재사용에 있어서 올바른 방법은, 여러 상황에서 동작 가능하고 쉽게 조합할수 잇는 **응집력 높은 객체**를 개발/사용하는 것이다.(동시에 결합력은 낮은!)

---

### 상속이 좋은 선택인 경우

: 상속이 양날의 검인 이유는부모 클래스를 쉽게 전수 받을수 있다는 장점과 동시에 너무 많은 기능을 가질 수 있어 사용자의 혼란을 가중시킬 수 있다는 단점도 동시에 존재하기 때문이다.

- 상속의 적용이 적절하지 않은 경우
    - 부모 클래스가 막연한 정의와 너무 많은 책임을 가짐.
    - 자식 클래스는 부모 클래스의 적절한 구체화가 아님.
- 상속의 적용이 잘 된 경우(일반적 클래스를 전문화/세부 추상화)
    - 부모 클래스의 기능을 모두 필요로 하면서 구체적인 몇가지 기능을 자식 클래스에서 추가하는 경우. i.e) (부모)BaseHTTPRequestHandler (자식)SimpleHTTPRequestHandler
    - 객체에 인터페이스 방식을 강제하고자 할때 구현 하지 않은 추상적인 부모 클래스를 만들고, 이 클래스를 상속하는 자식 클래스에서 적절한 구현을 하는 경우.
    - 파이썬의 모든 예외는 표준 예외 Exception에서 파생됨. i.e.) (조부모)IOError (부모)RequestException (자식)HTTPError

### 상속 안티패턴

:도메인 문제를 해결하기 위해 적절한 데이터 구조를 만든 다음에 이 데이터 구조를 사용하는 객체를 만들지 않고 데이터 구조 자체를 객체로 만드는 경우

    class TransactionalPolicy(collections.UserDict):
        """잘못된 상속의 예"""
    
        def change_in_policy(self, customer_id, **new_policy_data):
            self[customer_id].update(**new_policy_data)
    
    >>> policy = TransactionalPolicy({
    					"client001":{
    							"fee":1000.0, 
    							"expiration_date":datetime(2020,1,3),
    					}
    		})
    >>> policy["client001"]
    {"fee":1000.0, "expiration_date":datetime.datetime(2020,1,3,0,0)}
    
    >>> policy.change_in_policy("client001", expiration_date=datetime(2020,1,4))
    >>> policy["client001"]
    {"fee":1000.0, "expiration_date":datetime.datetime(2020,1,4,0,0)}
    
    >>>dir(policy)
    [# 모든 매직 메서드는 생략...
    	'change_in_policy','clear','copy','data','fromkeys','get','items','keys','pop',
    	'popitem','setdefault','update','values']

- 위 코드의 문제점
    1. TransactionalPolicy 이름을 통해 사전 타입이라는 것을 파악하기 어렵고, 노출된 public 메서드를 통해 부적절하게 전문화된 이상한 계층 구조라고 사용자들이 생각 할 것임.
    2. 불필요해보이는 pop, items와 같은 public 메서드들이 그대로 노출되어 잇어서 사용자들이 임의로 호출할 수 있음.
- 컴포지션을 활용한 개선

: dictionary를 private 속성에 저장하고 __getitem**__**()으로 딕셔너리의 프록시를 만들고 추가 필요 public 메서드를 구현함.

    class TransactionalPolicy:
        """컴포지션을 사용한 리팩토링"""
    
        def __init__(self, policy_data, **extra_data):
            self._data = {**policy_data, **extra_data}
    
        def change_in_policy(self, customer_id, **new_policy_data):
            self._data[customer_id].update(**new_policy_data)
    
        def __getitem__(self, customer_id):
            return self._data[customer_id]
    
        def __len__(self):
            return len(self._data)

### 파이썬의 다중상속

다중 상속을 지원하는 파이썬은 자칫 잘못 구현하면 여러가지 디자인 문제를 유발한다.

- 메서드 결정 순서(MRO)

    :아래 다이어 그램을 통해 다중 상속 구조를 이해해보자

    ![Chapter%203/Untitled.png](Chapter%203/Untitled.png)

    - 최상위 속성은 module_name 속성을 가지며 __str__메서드를 구현한다. 중간 1, 2 모듈중에 어떤 것이 하단 A12클래스의 메서드가 되는지 아래의 코드로 확인해보자.

        class BaseModule:
            module_name = "top"
        
            def __init__(self, module_name):
                self.name = module_name
        
            def __str__(self):
                return f"{self.module_name}:{self.name}"
        
        
        class BaseModule1(BaseModule):
            module_name = "module-1"
        
        
        class BaseModule2(BaseModule):
            module_name = "module-2"
        
        
        class BaseModule3(BaseModule):
            module_name = "module-3"
        
        
        class ConcreteModuleA12(BaseModule1, BaseModule2):
            """1과 2 확장"""
        
        
        class ConcreteModuleB23(BaseModule2, BaseModule3):
            """2와 3 확장"""
        
        >>> str(ConcreteModuleA12("test"))
        'module-1:test'
        # 충돌발생X, Python에서는 메서드가 호출되는 방식을 정의하는
        # MRO 또는 C3 Linearization 알고리즘을 활용하여 문제를 해결함.
        # https://en.wikipedia.org/wiki/C3_linearization
        
        # 직접 클래스 결정 순서 확인
        >>> [cls.__name__ for cls in ConcreteModuleA12.mro()] 
        ['ConcreteModuleA12','BaseModule1','BaseModule2','BaseModule','object']

- 믹스인(mixin)
    - 정의: 코드를 재사용하기 위해 일반적인 행동을 캡슐화해놓은 기본 클래스를 말한다.
    - 특징: 믹스인 클래스는 그 자체로 유용하지 않으며 대부분 클래스에 정의된 메서드나 속성에 의존한다.
    - 용법 : 다른 클래스와 함께 믹스인 클래스를 다중 상속하여 믹스인 내부 메서드/속성을 사용함.

        class BaseTokenizer:
            """하이픈으로 구분된 값을 반환하는 parser"""
        
            def __init__(self, str_token):
                self.str_token = str_token
        
            def __iter__(self):
                yield from self.str_token.split("-")
        
        >>> tk = BaseTokenizer("28a2320b-fd3f-4627-9792-a2b38e3c46b0")
        >>> list(tk)
        ['28a2320b', 'fd3f', '4627', '9792', 'a2b38e3c46b0']

    - 많은 클래스가 이미 해당 클래스를 확장했고 자식 클래스를 일일이 수정하고 싶지 않다고 가정한 상황에서 값을 대문자로 변환해 보자.

        class UpperIterableMixin:
            def __iter__(self):
                return map(str.upper, super().__iter__())
        
        class Tokenizer(UpperIterableMixin, BaseTokenizer):
        		"""
        		1. Tokenizer는 UpperIterableMixin에서 __iter__를 호출
        		2. super()를 호출하여 다음 클래스 BaseTokenizer에 위임
        			* 이때 이미 대문자를 전달 함.
        		"""
        		pass
        
        >>> tk = Tokenizer("28a2320b-fd3f-4627-9792-a2b38e3c46b0")
        >>> list(tk)
        ['28A2320B', 'FD3F', '4627', '9792', 'A2B38E3C46B0']
        

    - 이러한 유형의 혼합은 일종의 데코레이터 역할을 함.

## 6. 함수와 메서드의 인자(Arguments in functions and methods)

 함수의 인자 전달 매커니즘과 SW 개발 모범사례에서 발견되는 일반적인 원칙을 살펴본다.

### 파이썬의 함수 인자 동작방식

- 인자는 함수에 어떻게 복사되는가
    - 파이썬에서는 모든 인자가 값에 의해 전달된다. 즉 함수에 값을 전달하면 함수의 변수에 할당되고 나중에 사용된다.
    - 만약 변경가능한 객체를 전달하고 함수 내부에서 값을 변경하면 결과에서 실제 값이 변경될 수 있다.

        >>> def f(arg):
        >>>     arg += " in function"
        >>>     print(arg)
        
        >>> immu = "hello"
        >>> f(immu)
        hello in function
        
        >>> mut = list("hello")
        >>> immu
        'hello'
        
        >>> f(mut)
        ['h','e','l','l',...,'n']
        
        >>> mut
        ['h','e','l','l',...,'n']

    ***저자) 함수 인자를 변경하지 말아라. 최대한 함수에서 발생할 수 있는 부작용을 줄여야 한다.***

- 가변인자
    - 별표(*, **)를 통해 여러 인자를 패킹하여 함수에 전달하고 부분적으로 언패킹 할 수 있다.

        >>> l = [1,2,3]
        >>> f(*l)
        1
        2
        3
        
        >>> def show(e, rest):
        		    print("요소 : {0} - 나머지: {1}".format(e, rest))
        
        >>> first, *rest = [1,2,3,4,5]
        >>> show(first, rest)
        요소: 1 - 나머지: [2,3,4,5]
        
        >>> *rest, last = range(6)
        >>> show(last, rest)
        요소: 5 - 나머지: [0,1,2,3,4]
        
        >>> first, *middle, last = range(6)
        >>> first
        0
        >>> middle
        [1,2,3,4]
        >>> last
        5
        
        >>> first, last, *empty = (1, 2)
        >>> first
        1
        >>> last
        2
        >>> empty
        []

    - "반복"은 변수 언패킹을 사용하기에 적절한 기능이다. 아래는 데이터베이스 결과를 리스트로 받는 함수를 가정할때, 언패킹을 사용/미사용 할때의 코드의 차이를 보여준다.

        USERS = [(i, f"first_name_{i}", "last_name_{i}") for i in range(1_000)]
        
        
        class User:
            def __init__(self, user_id, first_name, last_name):
                self.user_id = user_id
                self.first_name = first_name
                self.last_name = last_name
        
        
        def bad_users_from_rows(dbrows) -> list:
            """DB 결과에서 사용자를 생성하는 파이썬스럽지 않은 예시"""
            return [User(row[0], row[1], row[2]) for row in dbrows]
        
        
        def users_from_rows(dbrows) -> list:
            """DB행에서 사용자 생성: 가독성이 좋음"""
            return [
                User(user_id, first_name, last_name)
                for (user_id, first_name, last_name) in dbrows
            ]

### 함수 인자의 개수

: 함수가 너무 많은 인자를 가진다면, 나쁜 디자인일 가능성이 높다. 이런 경우 일반적으로...

1. 구체화(전달하는 모든 인자를 포함하는 새로운 객체를 만듦)를 통해 일반적 SW 디자인의 원칙을 사용한다.
2. 가변인자나 키워드 인자를 사용하여 동적 서명을 가진 함수를 만든다. 단, 매우 동적이어서 유지보수가 어렵기 때문에 남용하지 않도록 주의한다.
3. 여러 작은 (한가지 기능을 담당하는)함수로 분리한다.
- 함수 인자와 결합력
    - 함수의 인자가 많을수록 호출하기 위한 정보를 수집하기가 점점 더 어려워 진다.
    - 함수의 추상화가 너무 적으면 다른 환경에서 사용하기 어렵거나(재사용성↓), 다른 함수에 지나치게 의존적이 된다.
    - 함수가 너무 많은 인자를 가진다면, 나쁜 디자인일 가능성이 높다.
- 많은 인자를 취하는 작은 함수의 서명
    - 공통 객체에 파라미터 대부분이 포함되어 있는 경우 리팩토링 하기

        track_request(request.headers, request.ip_addr, request.request_id)
        # 모든 파라미터가 request와 관련이 있으므로 그냥 request를 파라미터로 
        # 전달하는 것으로 변경한다. 단, 함수가 전달받은 객체를 변경하지 않도록 한다.

    - 하나의 객체에 파라미터를 담아 전달한다. 파라미터 그룹핑이라고 한다.
    - 함수의 서명을 변경하여 다양한 인자를 허용한다. 단, 인터페이스에 대한 문서화를 하고 정확하게 사용했는지 확인해야 한다.
    - *arg, **kwarg를 사용한다. 단, 이 경우 서명을 잃어버리고 가독성을 거의 상실하므로 사용에 주의한다.

## 7. 소프트웨어 디자인 우수 사례 결론(Final remarks on good practices for software design)

### 소프트웨어의 독립성(Orthogonality)

: SW의 런타임 구조 측면에서 직교란, 변경(또는 부작용)을 내부 문제로 만드는 것이다. 예를들어 어떤 객체의 메서드를 호출하는 것이 다른 관련없는 객체의 내부 상태를 변경해서는 안된다. 

- 아래의 코드에서, 가격 계산함수와 표시함수는 서로 독립이다. 이를 알고 있다면, 둘중 하나의 함수를 쉽게 변경할 수 있으며 두 함수에 대한 단위 테스트가 성공하면 전체 테스트도 필요치 않다.

    # 가격 계산함수
    def calculate_price(base_price: float, tax: float, discount: float) -> float:
        return (base_price * (1 + tax)) * (1 - discount)
    
    # 가격 표시함수
    def show_price(price: float) -> str:
        return "$ {0:,.2f}".format(price)
    
    
    def str_final_price(
        base_price: float, tax: float, discount: float, fmt_function=str
    ) -> str:
        return fmt_function(calculate_price(base_price, tax, discount))
    
    >>> str_final_price(10, 0.2, 0.5)
    '0.6'
    
    >>> str_final_price(1000, 0.2, 0)
    '1200.0'
    
    >>> str_final_price(1000, 0.2, 0.1, fmt_function=show_price)
    '$ 1,080.00'

### 코드 구조

: 팀의 작업 효율성과 유지보수성을 위해 코드를 구조화 한다.

- 유사한 컴포넌트끼리 정리하여 구조화 한다.
- __init__.py를 가진 디렉토리를 통해 파이썬 패키지를 만들면, 코드간의 종속성이 있어도 전체적인 호환성을 유지한다.(__init__.py 파일에 다른 파일에 있던 모든 정의를 가져올 수 있다)
    - *모듈을 import할때 구문을 분석하고 메모리에 로드할 객체가 줄어든다.*
    - *의존성이 줄었기 때문에 더 적은 모듈만 가져오면 된다.*
- config에 정의가 필요한 상수를 정의하고 일괄 import하여 정보를 중앙화 한다.

자세한 내용은 10장에서 다룰예정.

## 요약

1. 고품질 SW를 만들기 위한 핵심은 코드도 디자인의 일부라는 것을 이해하는 것이다.
2. DbC(계약에 의한 디자인)을 적용하면 주어진 조건 하에서 동작이 보장되는 컴포넌트를 만들수 있다.
    1. 오류가 발생하면 원인이 무엇이며 어떤 부분이 계약을 파기했는지 명확히 알수 있다.
    2. 위와 같은 역할분담은 효과적인 디버깅에 유리하다.
3. 방어적 프로그래밍을 통해 악의적인 의도를 가진 또는 잘못된 입력으로부터 스스로를 보호하면 개별 컴포넌트를 더욱 강력하게 만들수 있다.
4. 2, 3번 모두 Assertion을 올바르게 사용해야 한다. 프로그램 흐름제어 용도나 예외에서 처리하기 위한 용도로 쓰는것은 부적절하다.
5. 예외는 언제 어떻게 사용해야 하는지는 아는것이 중요하다. 제어흐룸 수단으로 쓰는것은 부적절하다.
6. OOP디자인에서는 부모 자식클래스간의 적절한 옵션을 사용하는 것이 중요하다. 또한 파이썬의 높은 동적 특성으로 발생하는 안티 패턴을 피해야 한다.
7. 파이썬의 특수성을 고려한 파라미터 갯수 관리가 필요하다.
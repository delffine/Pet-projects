------ Запрос на пострение матриц кортного анализа -------
параметры запроса:
{{interval_from}}, {{interval_to}} - границы интервала дат
{{col}} - выбор выводимного показателя через параметр


WITH
t1 as (SELECT *,  
		EXTRACT(month FROM MIN(tr_date) OVER (PARTITION BY user_id))::int as ch
    FROM public.simplegoods
    WHERE status = 'Завершена'
        AND oper_sum < 25000
        AND tr_date BETWEEN {{interval_from}} AND {{interval_to}}), 
t2 as (
    SELECT ch, (TR_month::int-ch+1) as ml,
		SUM(oper_sum) as opsum,
		COUNT(DISTINCT user_id) as users,
		COUNT(tr_id) as trcount,
		SUM(oper_sum) / COUNT(tr_id) as avgsum
    FROM t1 
    GROUP BY ch, tr_month
    ORDER BY ch, tr_month),
t3 as (SELECT ch, ml,
    CASE 
		WHEN {{col}} = 'oper_sum' THEN opsum
		WHEN {{col}} = 'users' THEN users
		WHEN {{col}} = 'trcount' THEN trcount
		WHEN {{col}} = 'avgsum' THEN avgsum
		WHEN {{col}} = 'cumsum' THEN SUM(opsum) OVER(PARTITION BY ch ORDER BY ml ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / MAX(users) OVER (PARTITION BY ch)
		WHEN {{col}} = 'cr' THEN 100 * users / MAX(users)  OVER (PARTITION BY ch)
    END as valcol
    FROM t2)

SELECT c1.ml as "Месяц жизни", ch1, ch2, ch3, ch4, ch5, ch6, ch7 FROM (SELECT ml, valcol as ch1 FROM t3 WHERE ch = 1) as c1
FULL JOIN 
(SELECT ml, valcol as ch2 FROM t3 WHERE ch = 2) as c2 ON c1.ml = c2.ml
FULL JOIN 
(SELECT ml, valcol as ch3 FROM t3 WHERE ch = 3) as c3 ON c1.ml = c3.ml
FULL JOIN 
(SELECT ml, valcol as ch4 FROM t3 WHERE ch = 4) as c4 ON c1.ml = c4.ml
FULL JOIN 
(SELECT ml, valcol as ch5 FROM t3 WHERE ch = 5) as c5 ON c1.ml = c5.ml
FULL JOIN 
(SELECT ml, valcol as ch6 FROM t3 WHERE ch = 6) as c6 ON c1.ml = c6.ml
FULL JOIN 
(SELECT ml, valcol as ch7 FROM t3 WHERE ch = 7) as c7 ON c1.ml = c7.ml



------ Запрос на пострение матриц RFM анализа -------
параметры запроса:
{{interval_from}}, {{interval_to}} - границы интервала дат
{{R1}}, {{R2}} - границы рангов R
{{F1}}, {{F2}} - границы рангов F
{{M1}}, {{M2}} - границы рангов M
{{col}} - выбор выводимного показателя через параметр
WITH
t1 as (SELECT user_id, 
    1 as users,
    SUM(oper_sum) as opsum, 
    count(tr_id) as trcount, 
    MIN(tr_date) as firstdate, 
    MAX(tr_date) as lastdate 
FROM public.simplegoods
WHERE status = 'Завершена' AND tr_date BETWEEN {{interval_from}} AND {{interval_to}}
GROUP BY user_id),
t2 as (SELECT user_id, 
    users, 
    trcount, 
    opsum, 
    '2024-08-01'::date - lastdate as days_ago,
    (lastdate - firstdate) / 30 + 1 as mon_on,
    trcount::real / ((lastdate - firstdate) / 30 + 1) as freq
FROM t1),
t3 as (SELECT *, 
    CASE 
        WHEN days_ago > {{R2}} THEN 'R3' 
        WHEN days_ago < {{R1}} THEN 'R1' 
        ELSE 'R2' END as R, 
    CASE 
        WHEN freq > {{F2}} THEN 'F1' 
        WHEN freq < {{F1}} THEN 'F3' 
        ELSE 'F2' END as F, 
    CASE 
        WHEN opsum > {{M2}} THEN 'M1' 
        WHEN opsum < {{M1}} THEN 'M3' 
        ELSE 'M2' END as M 
FROM t2),
t4 as (SELECT *, CONCAT(R, F) as RF  FROM t3)

SELECT RF, 
    SUM(CASE WHEN M='M1' THEN (
            CASE 
            WHEN {{col}}='opsum' THEN opsum 
            WHEN {{col}}='trcount' THEN trcount
            WHEN {{col}}='users' THEN users            
            END)
        ELSE 0    
        END) as "M1", 
    SUM(CASE WHEN M='M2' THEN (
            CASE 
            WHEN {{col}}='opsum' THEN opsum 
            WHEN {{col}}='trcount' THEN trcount
            WHEN {{col}}='users' THEN users            
            END)
        ELSE 0             
        END) as "M2", 
    SUM(CASE WHEN M='M3' THEN (
            CASE 
            WHEN {{col}}='opsum' THEN opsum 
            WHEN {{col}}='trcount' THEN trcount
            WHEN {{col}}='users' THEN users            
            END)
        ELSE 0             
        END) as "M3"
 FROM t4 
 GROUP BY RF
 ORDER BY RF


---------- Запрос для графика пользователи, покупатели, подписчки нарастаранием ----------
параметры запроса:
{{interval_from}}, {{interval_to}} - границы интервала дат
WITH
t1 as (SELECT * 
		FROM public.simplegoods 
		WHERE tr_date BETWEEN {{interval_from}} AND {{interval_to}}
		)

SELECT sg1.tr_date as Дата, 
(SELECT COUNT(DISTINCT sg2.user_id)
	FROM t1 as sg2
	WHERE tr_date <= sg1.tr_date
) AS Пользовтели,
(SELECT COUNT(DISTINCT sg2.user_id)
	FROM t1 as sg2
	WHERE NOT sg2.subscr ISNULL AND tr_date <= sg1.tr_date
) AS Подписчики,
(SELECT COUNT(DISTINCT sg2.user_id)
	FROM t1 as sg2
	WHERE type='Покупка' AND tr_date <= sg1.tr_date
) AS Покупатели
FROM t1 AS sg1
ORDER BY sg1.tr_date

---------- Запрос для кольцовой диаграммы пользователи по ролям ----------
параметры запроса:
{{interval_from}}, {{interval_to}} - границы интервала дат
WITH
t1 as (SELECT user_id, 
    SUM(CASE WHEN NOT subscr ISNULL THEN 1 ELSE 0 END) as sub,
    SUM(CASE WHEN type='Покупка' THEN 1 ELSE 0 END) as buy    
FROM public.simplegoods
WHERE status = 'Завершена' AND tr_date BETWEEN {{interval_from}} AND {{interval_to}}
GROUP BY user_id)


SELECT 'Подписчики' AS tt, COUNT(*) FILTER (WHERE sub > 0 AND buy = 0) FROM t1
UNION
SELECT 'Покупители', COUNT(*) FILTER (WHERE buy > 0 AND sub = 0) FROM t1
UNION
SELECT 'Доноры', COUNT(*) FILTER (WHERE buy = 0 AND sub = 0) FROM t1
UNION
SELECT 'Покуп & Подпис', COUNT(*) FILTER (WHERE buy > 0 AND sub > 0) FROM t1

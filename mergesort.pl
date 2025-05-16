
partition([], [], []).
partition([X], [X], []).
partition([H1, H2 | T], [H1 | T1], [H2 | T2]) :-  partition(T, T1, T2).

merge(X, [], X).
merge([],X, X).
merge([H1 | T1], [H2 | T2], [H1 | T]) :-
  H1 =< H2,
  merge(T1, [H2 | T2], T).  
merge([H1 | T1], [H2 | T2], [H2 | T]) :-
  H1 > H2,
  merge([H1 | T1], T2,T).

mergesort([], []).
mergesort([X], [X]).
mergesort([H1, H2 | T], A) :-
  partition([H1, H2 | T], L1, L2),
  mergesort(L1, TEMP1),
  mergesort(L2, TEMP2),
  merge(TEMP1, TEMP2, A).

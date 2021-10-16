ballpos=[40,30,35];
ballradius=5;
ball = fspecial3('gaussian',2*ballradius+1);

A = zeros(100,100,100);
B = A;

shift = [10,10,10];

A(ballpos(1)-ballradius:ballpos(1)+ballradius,ballpos(2)-ballradius:ballpos(2)+ballradius,ballpos(3)-ballradius:ballpos(3)+ballradius)=ball;
ballpos=ballpos+shift;
B(ballpos(1)-ballradius:ballpos(1)+ballradius,ballpos(2)-ballradius:ballpos(2)+ballradius,ballpos(3)-ballradius:ballpos(3)+ballradius)=ball;

%figure, imshow(max(A,[],3),[])
%figure, imshow(max(B,[],3),[])

A = A  + normrnd(0,0.0005,size(A));
B = B  + normrnd(0,0.0005,size(B));

figure, imshow(A(:,:,35),[])
figure, imshow(B(:,:,45),[])
xcorr2fft(A,B)
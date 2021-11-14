function [VX,VY,VZ,shiftx,shifty,shiftz] = GetPIV3d(im1,im2,X1,Y1,Z1,EdgeLength)
    

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %
    %   GetPIV computes PIV flow field estimate based on image1 (im1) and
    %   image2 (im2) using the Phase Correlation method implemented in xcorr3fft. 
    %   im1 & im2 are assumed to have the same dimensions. The grid
    %   X1,Y1,Z1
    %   is assmued to be contained in the image domain with finite
    %   EdgeLength defining size of PIV box. 
    %   Output are components of the flow fiel on the grid
    %   
    %   Written by: Sebastian J Streichan, KITP, February 01, 2013
    %
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    
    si      = size(im1);
    nb      = ceil(si/EdgeLength);
    counter = 0;
    shiftx  = zeros(1,nb(1)*nb(2)*nb(3));
    shifty  = shiftx;
    shiftz  = shiftx;
    x       = shiftx;
    y       = shifty;
    z       = shiftx;
    window  = 15;
    
    for i = 1 : nb(1)
        for j = 1 : nb(2)
            for k = 1 : nb(3)
            
                % cut a cube out of the image
                counter = counter+1;
                temp1 = im1(max(1,((i-1)*EdgeLength-window+1)):min((i+1)*EdgeLength+window,si(1)),...
                           (max(1,(j-1)*EdgeLength-window+1)):min((j+1)*EdgeLength+window,si(2)),...
                           (max(1,(k-1)*EdgeLength-window+1)):min((k+1)*EdgeLength+window,si(3)));
                temp2 = im2(max(1,((i-1)*EdgeLength-window+1)):min((i+1)*EdgeLength+window,si(1)),...
                           (max(1,(j-1)*EdgeLength-window+1)):min((j+1)*EdgeLength+window,si(2)),...
                           (max(1,(k-1)*EdgeLength-window+1)):min((k+1)*EdgeLength+window,si(3)));   

                [shiftx(counter),shifty(counter),shiftz(counter)] = xcorr3fft(temp1,temp2);
                x(counter) = (i-.5)*EdgeLength;
                y(counter) = (j-.5)*EdgeLength;
                z(counter) = (k-.5)*EdgeLength;
            end
        end
    end
    
    % Put the flow field on a grid 
    VX  = griddata(x,y,z,shiftx,X1,Y1,Z1);
    VY  = griddata(x,y,z,shifty,X1,Y1,Z1);
    VZ  = griddata(x,y,z,shiftz,X1,Y1,Z1);
end
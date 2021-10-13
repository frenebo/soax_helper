%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%   Using GetPIV we computes the flow field estimate based on an image sequence 
%   im1 & im2 are assumed to have the same dimensions. The grid X1,Y1
%   is assmued to be contained in the image domain with finite
%   EdgeLength defining size of PIV box. 
%   This script generates a movie displaying the original image with flow
%   field overlayed. 
%   
%   Written by: Sebastian J Streichan, KITP, February 14, 2013
%   Modified to 3d by: Le Yan, KITP, August 6, 2016
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
addpath(genpath('/Users/raymondadkins/Desktop/drive-download-20191011T235916Z-001/'));
Name   = 'TP%01d_Ch2_Ill0_Ang0,90,180,270.tif';

velfolder='PIV/'; %director folder
if isfolder(velfolder)~=1
    mkdir(velfolder);
end
 
NTimes   = 4;
timestart = 1;
EdgeLength  = 12;   % Length of box edges in pixels; 
%EdgeLength2 = 1;    % Length of box edges in interpolated field
isf         = 1;   % image scaling factor. 
step        = 1;    % step in timeframes.
smooth      = 0;    % setto 1 if gaussian smoothing is desired
KernelSize  = 7;    % Smoothing kernel size
sigma       = .8;  % standard deviation of gaussian kernel
im1 = imread(sprintf(Name,timestart));
im1 = imresize(im1,isf,'bicubic');
stackSize = length(imfinfo(sprintf(Name,timestart)));
slice_index = 1 : stackSize;
for slice = 1 : 1: length(slice_index)
    temp_im = imread(sprintf(Name,timestart),slice_index(slice));
    im1(:,:,slice)     = imresize(temp_im,isf,'bicubic'); % rescale image if desired
end
% define the grid on which to compute the flow field
[X1,Y1,Z1] = meshgrid(EdgeLength/2:EdgeLength:size(im1,1)-EdgeLength/2,EdgeLength/2:EdgeLength:size(im1,2)-EdgeLength/2,EdgeLength/2:EdgeLength/1:size(im1,3)-EdgeLength/2); 
%% 
for time = timestart: timestart+NTimes
    % read the image and scale
    
    tp_1_name = sprintf(Name,time);
    tp_2_name = sprintf(Name,time+step);

    % read Image stacks; and down sample; 
    if time == 0
        stackSize = length(imfinfo(tp_1_name));
    end
    slice_index = 1 : isf : stackSize;
    for slice = 1 : length(slice_index)
        temp_im = imread(tp_1_name,slice_index(slice));
        im1(:,:,slice)     = imresize(temp_im,isf,'bicubic'); % rescale image if desired

        temp_im = imread(tp_2_name,slice_index(slice));
        im2(:,:,slice)     = imresize(temp_im,isf,'bicubic'); % rescale image if desired
    end

    % compute the piv flow field
    [VY,VX,VZ] = GetPIV3d(im1,im2,X1,Y1,Z1,EdgeLength); 

    % smooth if desired
%     if smooth == 1
%         VX  = GaussSmooth(VX, sigma);
%         VY  = GaussSmooth(VY, sigma);
%         VZ  = GaussSmooth(VZ, sigma);
%     end
% 
    mid = floor(length(slice_index)/2);
%     % Display image and overlay flow field.
    tmp = im1(:,:, mid:mid+10);
    [f,x] = ecdf(tmp(:));
    lb = x(find(f >.1,1,'first'));
    ub = x(find(f <.98,1,'last'))+1000;

    imshow(10*tmp(:, :, 4))
    hold on 
    quiver(Y1(1:1:end,1:1:end,4),X1(1:1:end,1:1:end,4),VX(1:1:end,1:1:end,4),VY(1:1:end,1:1:end,4),1,'g')
    h = getframe;
    imwrite(h(1).cdata,'test.tif','tiff','compression','none','writemode','append')
    mov(time-timestart+1)    = getframe; 
    save(sprintf('PIV/vel_%03d.mat',time),'VX','VY','VZ');
%     direcVTKfile = ['TP', num2str(time), '_Velocity.vtk'];
%     vtkwrite(['PIV/', direcVTKfile],'structured_grid',reshape(round(X1), numel(X1), 1),reshape(round(Y1), numel(X1), 1),reshape(round(Z1), numel(X1), 1),'vectors','velocity',reshape(VY,numel(X1),1), reshape(VX, numel(X1),1), reshape(VZ,numel(X1),1))
%     
%     
%     Orientation_Ray=[reshape(round(X1), numel(X1), 1),reshape(round(Y1), numel(X1), 1),reshape(round(Z1), numel(X1), 1),reshape(VY,numel(X1),1), reshape(VX, numel(X1),1), reshape(VZ,numel(X1),1)];
%     fid = fopen(['PIV/Velocity',num2str(time), '.bin'], 'W');
%     fprintf(fid, '%u\t%u\t%u\t%f\t%f\t%f\t\n', Orientation_Ray.');
%     fclose(fid);
    
    
    
end
%play a movie;
implay(mov) 


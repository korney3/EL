def plot_graph(x,y,plot_title = None,plot_props=None,x_props=None,y_props=None,figsize=None):
    """Plots simple graph with changable title, x/y labels and plot style
    
    Parameters:
    x/y_props (dict) - {'title':str, 'fontsize_title':int, 'fontsize_ticks':int, 'ticks_orientation':int}
    plot_title (dict) - {'title:'str, 'fontsize': int}
    plot_props (str) - (for ex. 'ro' or 'g*')
    
    Returns:
    figure, axis
    """
    import matplotlib.pyplot as plt
    if figsize is not None and ((figsize and type(figsize)) is list or (figsize and type(figsize)) is tuple):
        if len(figsize)==2:
            x_size,y_size = figsize
            fig,ax = plt.subplots(figsize=(x_size,y_size))
        else:
            fig,ax = plt.subplots()
    else:
        fig,ax = plt.subplots()
    if plot_props is not None:
        ax.plot(x,y,plot_props)
    else:
        ax.plot(x,y)
    if plot_title is not None and ((plot_title and type(plot_title)) is dict):
        if 'title' in plot_title.keys():
            if 'fontsize' in plot_title.keys():
                ax.set_title(plot_title['title'],fontsize=plot_title['fontsize'])
            else:
                ax.set_title(plot_title['title'])
    if x_props is not None and ((x_props and type(x_props)) is dict):
        if 'title' in x_props.keys():
            if 'fontsize_title' in x_props.keys():
                ax.set_xlabel(x_props['title'],fontsize=x_props['fontsize_title'])
            else:
                ax.set_xlabel(x_props['title'])
        if 'fontsize_ticks' in x_props.keys():
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(x_props['fontsize_ticks']) 
                # specify integer or one of preset strings, e.g.
                #tick.label.set_fontsize('x-small') 
                if 'ticks_orientation' in x_props.keys():
                    tick.label.set_rotation(x_props['ticks_orientation'])
    if y_props is not None and ((y_props and type(y_props)) is dict):
        if 'title' in y_props.keys():
            if 'fontsize_title' in y_props.keys():
                ax.set_ylabel(y_props['title'],fontsize=y_props['fontsize_title'])
            else:
                ax.set_ylabel(y_props['title'])
        if 'fontsize_ticks' in y_props.keys():
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(y_props['fontsize_ticks']) 
                # specify integer or one of preset strings, e.g.
                #tick.label.set_fontsize('x-small') 
                if 'ticks_orientation' in y_props.keys():
                    tick.label.set_rotation(y_props['ticks_orientation'])
    return fig,ax

def print_progress_stats(overall_iters, done_iters, errors_num=None, time_per_iteration=0, num_of_processes=1):
    """Prints statistic info about made/left iteration and time predictions
    
    Parameters:
    overall_iters (int) - number of iterations to be made
    done_iters (int) - number of completed iterations
    errors_num (int) - number of errors
    time_per_iteration (int) - mins spent on one iteration
    num_of_processes (int) - number of processes doing iterations
    
    Returns:
    -
    """
    import datetime
    now = datetime.datetime.now()
    print (now.strftime("%Y-%m-%d %H:%M:%S"))
    print('Number of processed iterations: ', done_iters, '(',round(done_iters/overall_iters*100),'% made)')
    if errors_num is not None:
        print('Number of errors: ',errors_num, '(',round(errors_num/done_iters*100),'% of errors)')
    else:
        pass
    print('Time left ~ ', round(time_per_iteration*(overall_iters-done_iters)/60/num_of_processes,3),' hours')
    print('Overall time spent ~ ', round(time_per_iteration*done_iters/num_of_processes/60, 3), ' hours')
    return
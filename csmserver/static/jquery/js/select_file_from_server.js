/**
 * This file is for selecting a single file from a server and directory.
 * The following js files must be included by the caller.
 *
 * <script src="/static/jquery-cookie-master/jquery.cookie.js"></script>
 * <script src="/static/bootbox-4.2.0/js/bootbox.js"></script>
 *
 * To retrieve the selected server ID
 *     $('#select_server').val()
 *
 * To retrieve the selected server name
 *     $('#select_server').text()
 *
 * To retrieve the selected server directory
 *     $('#select_server_directory').val()
 */

var select_server_spinner;
var select_file_spinner;


$(function() {

    select_server_spinner = $('#select-server-spinner');
    select_server_spinner.hide();

    select_file_spinner = $('#select-file-spinner');
    select_file_spinner.hide();

    $('#select-server-move-up').on('click', function(e) {
        retrieve_file_list(
            $('#select_server').val(),
            $('#select_server_directory'),
            get_parent_folder($('#select_server_directory').val()),
            $('#select_file'),
            true);
    });

    $('#select_server').on('change', function(e) {
        server_id = $('#select_server option:selected').val();
        if (server_id == -1) {
            $('#select_server_directory').html('');
        } else {
            retrieve_file_list(server_id, $('#select_server_directory'), '', $('#select_file'), true)
        }
    });

    $('#select_server_directory').on('change', function(e) {
        retrieve_file_list(
            $('#select_server').val(),
            $('#select_server_directory'),
            $('#select_server_directory').val(),
            $('#select_file'),
            false);
    });

    $('#select-server-reset-server-directory').on('click', function(e) {
        reset_server_directory(
            $('#select_server').val(),
            $('#select_server_directory'),
            $('#select_server_directory').val(),
            $('#select_file'),
            true);
    });

    function reset_server_directory(server_id, server_directory_selector, server_directory, file_selector, show_select_server_spinner) {
        if (server_directory != '') {
            bootbox.confirm('Reset the server directory to use the server repository base directory?', function(result) {
                if (result) {
                    retrieve_file_list(server_id, server_directory_selector, '', file_selector, show_select_server_spinner)
                }
            });
        }
    }

    function retrieve_file_list(server_id, server_directory_selector, server_directory, file_selector, show_select_server_spinner) {
      server_directory_selector.html('');
      server_directory_selector.append('<option value="' + server_directory + '">' + server_directory + '</option>');
      file_selector.html('');
      file_selector.append('<option value=""></option>');

      select_file_spinner.show();
      if (show_select_server_spinner) {
        select_server_spinner.show();
      }

      $.ajax({
          url: "/install/api/get_server_file_dict/" + server_id,
          dataType: 'json',
          data: {
            server_directory: server_directory
          },
          success: function(response) {
              if (response.status == 'Failed') {
                  bootbox.alert("NOTE: The selected server repository is not browsable by CSM Server.");
              } else {
                  $.each(response, function(index, element) {
                      populate_file_list(element, server_directory_selector, file_selector);
                  });
              }

              select_file_spinner.hide();
              if (show_select_server_spinner) {
                select_server_spinner.hide();
              }
          },
          error: function(XMLHttpRequest, textStatus, errorThrown) {
              bootbox.alert("Unable to list files. Server repository may not be visible by CSM Server.");
              select_file_spinner.hide();
              if (show_select_server_spinner) {
                select_server_spinner.hide();
              }
          }
      });
    }

    function populate_file_list(element, server_directory_selector, file_selector) {
        for (i = 0; i < element.length; i++) {
            var filename = element[i].filename;
            var is_directory = element[i].is_directory;

            if (is_directory == true) {
                server_directory_selector.append('<option value="' + filename + '">' + filename + '</option>');
            } else {
                file_selector.append('<option value="' + filename + '">' + filename + '</option>');
            }
        }
    }

});